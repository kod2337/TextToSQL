#!/usr/bin/env python3
"""
Direct server start script
"""
import sys
import os
sys.path.append('.')

import uvicorn
from src.api.app import create_app

if __name__ == "__main__":
    app = create_app()
    print("🚀 Starting server...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
