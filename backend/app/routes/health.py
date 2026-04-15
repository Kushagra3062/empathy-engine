from fastapi import APIRouter
import time
import os

router = APIRouter()

@router.get("/health")
async def health_check():

    return {
        "status": "online",
        "timestamp": time.time(),
        "services": {
            "database": "connected", 
            "tts_local": "available",
            "storage": "writable" if os.access(".", os.W_OK) else "readonly"
        },
        "version": "1.0.0"
    }
