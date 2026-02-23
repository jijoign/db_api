"""Run the FastAPI application."""
import sys
import uvicorn
from config import settings
from app.main import app

if __name__ == "__main__":
    # Disable reload when running as frozen executable (PyInstaller)
    # Reload watches for file changes, which doesn't work in bundled executables
    is_frozen = getattr(sys, 'frozen', False)
    
    uvicorn.run(
        app,  # Pass app object directly instead of string (required for PyInstaller)
        host=settings.host,
        port=settings.port,
        reload=settings.debug and not is_frozen
    )
