# 🧠 Text-to-SQL Assistant

A natural language AI assistant that converts user questions into **SQL queries** and executes them on a relational database.  
Example:  
> **Input:** *"Show me all orders from last month."*  
> **Output:** `SELECT * FROM orders WHERE order_date >= '2025-07-01' AND order_date < '2025-08-01';`

---

## 🚀 Features
- **Natural Language → SQL Conversion** using LLMs (LangChain + Hugging Face).  
- **Schema-Aware Prompting** → Assistant dynamically understands the database structure.  
- **Safe Query Execution** with SQL validation and error handling.  
- **REST API (FastAPI)** → Expose query functionality as a service.  
- **Database Support** → Works with SQLite (demo), extendable to Postgres/MySQL.  
- **Extensible** → Can add memory, follow-up queries, or integrate with BI dashboards.  

---

## 🛠️ Tech Stack
- **Python** (3.10+)  
- **LangChain** – LLM orchestration  
- **Hugging Face Transformers** – Open-source LLMs  
- **FastAPI** – REST API for serving queries  
- **SQLite / PostgreSQL** – Relational database  
- **SQLAlchemy** – ORM & schema handling  

---

## 📂 Project Structure
