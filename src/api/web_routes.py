"""
Web routes for serving the HTML interface
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

router = APIRouter()

# Get the web directory path
WEB_DIR = Path(__file__).parent.parent.parent / "web"
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"

def get_web_router() -> APIRouter:
    """Get the web interface router"""
    return router

@router.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main web interface"""
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(content="<h1>Web interface not found</h1>", status_code=404)

@router.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static files"""
    file_location = STATIC_DIR / file_path
    if file_location.exists() and file_location.is_file():
        return FileResponse(file_location)
    else:
        return HTMLResponse(content="File not found", status_code=404)
