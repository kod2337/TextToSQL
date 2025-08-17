// Text-to-SQL Assistant Web Interface with LangChain Support
class TextToSQLApp {
    constructor() {
        // Dynamically detect the API base URL
        this.apiBase = window.location.origin;
        this.conversationHistory = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkStatus();
        this.loadSchema();
        this.loadQuickStats();
    }

    bindEvents() {
        // Generate SQL button
        document.getElementById('generate-sql').addEventListener('click', () => {
            this.generateSQL();
        });
        
        // Clear memory button
        document.getElementById('clear-memory').addEventListener('click', () => {
            this.clearConversationMemory();
        });

        // Example buttons
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.getElementById('question-input').value = e.target.textContent.trim();
            });
        });

        // Copy SQL button
        document.getElementById('copy-sql').addEventListener('click', () => {
            this.copySQLToClipboard();
        });

        // Refresh buttons
        document.getElementById('refresh-status').addEventListener('click', () => {
            this.checkStatus();
        });

        document.getElementById('refresh-schema').addEventListener('click', () => {
            this.loadSchema();
        });

        // Enter key in textarea
        document.getElementById('question-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                this.generateSQL();
            }
        });
    }

    async checkStatus() {
        try {
            const response = await fetch(`${this.apiBase}/api/v1/health`);
            const data = await response.json();
            
            const statusIndicator = document.getElementById('status-indicator');
            const statusText = document.getElementById('status-text');
            const statusDot = statusIndicator.querySelector('.status-dot');
            
            // Remove existing status classes
            statusDot.classList.remove('status-healthy', 'status-degraded', 'status-error');
            
            if (data.status === 'healthy') {
                statusDot.classList.add('status-healthy');
                statusText.textContent = 'All systems operational';
            } else if (data.status === 'degraded') {
                statusDot.classList.add('status-degraded');
                statusText.textContent = 'Some services degraded';
            } else {
                statusDot.classList.add('status-error');
                statusText.textContent = 'Service issues detected';
            }
        } catch (error) {
            const statusIndicator = document.getElementById('status-indicator');
            const statusText = document.getElementById('status-text');
            const statusDot = statusIndicator.querySelector('.status-dot');
            
            statusDot.classList.remove('status-healthy', 'status-degraded');
            statusDot.classList.add('status-error');
            statusText.textContent = 'API unavailable';
        }
    }

    async loadSchema() {
        try {
            const response = await fetch(`${this.apiBase}/api/v1/schema`);
            const data = await response.json();
            
            const schemaContent = document.getElementById('schema-content');
            let html = '';
            
            Object.entries(data.tables || {}).forEach(([tableName, tableInfo]) => {
                html += `
                    <div class="mb-4 p-3 bg-gray-800 bg-opacity-50 rounded-lg">
                        <div class="font-semibold text-white flex items-center justify-between">
                            <span><i class="fas fa-table mr-2 text-cyan-400"></i>${tableName}</span>
                            <span class="text-xs text-gray-400">${tableInfo.row_count || 0} rows</span>
                        </div>
                        <div class="mt-2 text-gray-300 text-xs">
                            ${(tableInfo.columns || []).map(col => 
                                `<span class="inline-block bg-gray-700 px-2 py-1 rounded mr-1 mb-1">${col}</span>`
                            ).join('')}
                        </div>
                    </div>
                `;
            });
            
            schemaContent.innerHTML = html || '<div class="text-gray-400">No schema available</div>';
        } catch (error) {
            document.getElementById('schema-content').innerHTML = 
                '<div class="text-red-400">Failed to load schema</div>';
        }
    }

    async loadQuickStats() {
        try {
            const response = await fetch(`${this.apiBase}/api/v1/schema`);
            const data = await response.json();
            
            const quickStats = document.getElementById('quick-stats');
            const tableCount = data.table_count || 0;
            const totalRows = Object.values(data.tables || {})
                .reduce((sum, table) => sum + (table.row_count || 0), 0);
            
            quickStats.innerHTML = `
                <div class="flex justify-between text-white">
                    <span><i class="fas fa-table mr-2 text-cyan-400"></i>Tables:</span>
                    <span class="font-semibold">${tableCount}</span>
                </div>
                <div class="flex justify-between text-white">
                    <span><i class="fas fa-database mr-2 text-green-400"></i>Total Rows:</span>
                    <span class="font-semibold">${totalRows.toLocaleString()}</span>
                </div>
                <div class="flex justify-between text-white">
                    <span><i class="fas fa-brain mr-2 text-purple-400"></i>AI Model:</span>
                    <span class="font-semibold">Groq Llama3</span>
                </div>
            `;
        } catch (error) {
            document.getElementById('quick-stats').innerHTML = 
                '<div class="text-red-400">Failed to load stats</div>';
        }
    }

    async generateSQL() {
        const question = document.getElementById('question-input').value.trim();
        if (!question) {
            this.showError('Please enter a question');
            return;
        }

        const executeQuery = document.getElementById('execute-query').checked;
        const includeSchema = document.getElementById('include-schema').checked;
        
        // Show loading state
        const generateBtn = document.getElementById('generate-sql');
        const originalText = generateBtn.innerHTML;
        generateBtn.innerHTML = '<div class="loading-spinner"></div>Thinking...';
        generateBtn.disabled = true;

        // Hide previous results
        document.getElementById('results-section').style.display = 'none';
        document.getElementById('error-display').style.display = 'none';

        try {
            // Always use LangChain endpoint now
            const endpoint = `${this.apiBase}/api/v1/langchain/text-to-sql`;
                
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    execute_query: executeQuery,
                    include_schema: includeSchema
                })
            });

            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);
            
            if (data.success || data.sql) {
                this.displayResults(data, executeQuery);
                
                // Always add to conversation history since we always use LangChain
                this.conversationHistory.push({
                    question: question,
                    sql: data.sql?.sql_query || '',
                    natural_response: data.sql?.natural_language_response || '',
                    timestamp: new Date().toISOString()
                });
                this.updateConversationHistory();
            } else {
                this.showError(data.error || 'Unknown error occurred');
            }
        } catch (error) {
            this.showError(`Network error: ${error.message}`);
        } finally {
            // Restore button state
            generateBtn.innerHTML = originalText;
            generateBtn.disabled = false;
        }
    }

    async clearConversationMemory() {
        try {
            const response = await fetch(`${this.apiBase}/api/v1/langchain/memory/clear`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.conversationHistory = [];
                this.updateConversationHistory();
                this.showSuccess('Conversation memory cleared');
            } else {
                this.showError('Failed to clear memory');
            }
        } catch (error) {
            this.showError(`Error clearing memory: ${error.message}`);
        }
    }

    updateConversationHistory() {
        const historyDiv = document.getElementById('conversation-history');
        
        if (this.conversationHistory.length === 0) {
            historyDiv.innerHTML = '<div class="text-gray-400 text-sm">No conversation history</div>';
            return;
        }

        const html = this.conversationHistory.slice(-5).map((item, index) => `
            <div class="mb-3 p-3 bg-gray-800 bg-opacity-50 rounded-lg">
                <div class="text-sm text-gray-400 mb-1">${new Date(item.timestamp).toLocaleTimeString()}</div>
                <div class="text-white font-medium mb-2">${item.question}</div>
                ${item.natural_response ? `
                    <div class="text-blue-200 text-sm mb-2 bg-blue-900 bg-opacity-30 p-2 rounded">
                        <i class="fas fa-comment-dots mr-1"></i> ${item.natural_response.substring(0, 150)}${item.natural_response.length > 150 ? '...' : ''}
                    </div>
                ` : ''}
                <div class="text-gray-300 text-xs font-mono bg-gray-900 p-2 rounded">
                    ${item.sql || 'No SQL generated'}
                </div>
                ${item.analysis ? `
                    <div class="mt-2 text-gray-400 text-xs">
                        <strong>Analysis:</strong> ${item.analysis.substring(0, 100)}...
                    </div>
                ` : ''}
            </div>
        `).join('');
        
        historyDiv.innerHTML = html;
    }

    showSuccess(message) {
        const successDiv = document.getElementById('success-display') || this.createSuccessDisplay();
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        
        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 3000);
    }

    createSuccessDisplay() {
        const div = document.createElement('div');
        div.id = 'success-display';
        div.className = 'bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4';
        div.style.display = 'none';
        
        const resultsSection = document.getElementById('results-section');
        resultsSection.parentNode.insertBefore(div, resultsSection);
        
        return div;
    }

    displayResults(data, executeQuery, showAnalysis = false) {
        const resultsSection = document.getElementById('results-section');
        const sqlElement = document.getElementById('generated-sql');
        const metadataElement = document.getElementById('sql-metadata');
        const confidenceBadge = document.getElementById('confidence-badge');
        const naturalResponseSection = document.getElementById('natural-response-section');
        const naturalResponseContent = document.getElementById('natural-response-content');
        
        // Show natural language response if available
        if (data.sql.natural_language_response) {
            naturalResponseContent.textContent = data.sql.natural_language_response;
            naturalResponseSection.style.display = 'block';
        } else {
            naturalResponseSection.style.display = 'none';
        }
        
        // Display SQL
        sqlElement.textContent = data.sql.sql_query;
        Prism.highlightElement(sqlElement);
        
        // Display confidence
        const confidence = data.sql.confidence_score || 0;
        confidenceBadge.textContent = `${confidence.toFixed(1)}% confidence`;
        confidenceBadge.className = `ml-auto text-xs px-2 py-1 rounded-full ${
            confidence >= 80 ? 'bg-green-600' : 
            confidence >= 60 ? 'bg-yellow-600' : 'bg-red-600'
        } text-white`;
        
        // Display metadata
        metadataElement.innerHTML = `
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <span class="text-gray-400">Execution Time:</span>
                    <span class="text-white">${data.sql.execution_time_ms?.toFixed(2) || 0}ms</span>
                </div>
                <div>
                    <span class="text-gray-400">Method:</span>
                    <span class="text-white">LangChain AI</span>
                </div>
                ${data.sql.explanation ? `
                <div class="col-span-2">
                    <span class="text-gray-400">Technical Explanation:</span>
                    <div class="text-white text-sm mt-1">${data.sql.explanation}</div>
                </div>
                ` : ''}
            </div>
        `;
        
        // Display query results if executed
        const queryResults = document.getElementById('query-results');
        if (executeQuery && data.results) {
            this.displayQueryResults(data.results);
            queryResults.style.display = 'block';
        } else {
            queryResults.style.display = 'none';
        }
        
        resultsSection.style.display = 'block';
    }

    displayQueryResults(results) {
        const resultsContent = document.getElementById('results-content');
        const resultsBadge = document.getElementById('results-badge');
        
        resultsBadge.textContent = `${results.row_count} rows in ${results.execution_time_ms?.toFixed(2)}ms`;
        
        if (results.rows && results.rows.length > 0) {
            // Create table
            const columns = results.columns || Object.keys(results.rows[0]);
            let html = `
                <div class="sql-result-table">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="bg-gray-700">
                                ${columns.map(col => 
                                    `<th class="px-3 py-2 text-left text-white border-b border-gray-600">${col}</th>`
                                ).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${results.rows.slice(0, 100).map((row, index) => `
                                <tr class="${index % 2 === 0 ? 'bg-gray-800' : 'bg-gray-700'} bg-opacity-50">
                                    ${columns.map(col => {
                                        let value = row[col];
                                        if (value === null || value === undefined) {
                                            value = '<span class="text-gray-500 italic">null</span>';
                                        } else if (typeof value === 'object') {
                                            value = JSON.stringify(value);
                                        } else {
                                            value = String(value);
                                            if (value.length > 50) {
                                                value = value.substring(0, 50) + '...';
                                            }
                                        }
                                        return `<td class="px-3 py-2 text-gray-200 border-b border-gray-600">${value}</td>`;
                                    }).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
            
            if (results.rows.length > 100) {
                html += `<div class="mt-2 text-sm text-gray-400 text-center">Showing first 100 of ${results.row_count} rows</div>`;
            }
            
            resultsContent.innerHTML = html;
        } else {
            resultsContent.innerHTML = '<div class="text-gray-400 text-center py-4">No results returned</div>';
        }
    }

    showError(message) {
        const errorDisplay = document.getElementById('error-display');
        const errorContent = document.getElementById('error-content');
        
        errorContent.textContent = message;
        errorDisplay.style.display = 'block';
        
        // Hide results section
        document.getElementById('results-section').style.display = 'none';
    }

    copySQLToClipboard() {
        const sqlText = document.getElementById('generated-sql').textContent;
        navigator.clipboard.writeText(sqlText).then(() => {
            const copyBtn = document.getElementById('copy-sql');
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fas fa-check mr-1"></i>Copied!';
            copyBtn.classList.add('bg-green-600');
            
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
                copyBtn.classList.remove('bg-green-600');
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new TextToSQLApp();
});
