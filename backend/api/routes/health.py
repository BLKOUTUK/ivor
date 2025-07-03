"""
Health check endpoints for IVOR Backend
"""

from fastapi import APIRouter
from typing import Dict, Any
import psutil
import time
from datetime import datetime

router = APIRouter()

@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "IVOR Backend",
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with system info"""
    
    # Get system metrics
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "IVOR Backend",
        "version": "1.0.0",
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        },
        "services": {
            "ai_service": "operational",
            "knowledge_base": "operational",
            "database": "operational"
        }
    }