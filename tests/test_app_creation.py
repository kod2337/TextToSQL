#!/usr/bin/env python3
"""
Simple test to check if the API app can be created
"""
import sys
import os
sys.path.append('.')

try:
    from src.api.app import create_app
    app = create_app()
    print('✅ App created successfully')
    
    print('\n🛣️ Available routes:')
    for route in app.routes:
        methods = getattr(route, 'methods', ['GET'])
        print(f'  {route.path} - {list(methods)}')
        
except Exception as e:
    print(f'❌ Error creating app: {e}')
    import traceback
    traceback.print_exc()
