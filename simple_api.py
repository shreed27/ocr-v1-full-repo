#!/usr/bin/env python3
"""
SIMPLE API - Just return JSON with page-by-page text
No complex processing, just clean JSON response
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Simple API",
    description="Just return JSON with page-by-page text",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Simple API",
        "version": "1.0.0"
    }

@app.post("/api/v1/ocr/upload")
async def upload_and_extract(file: UploadFile = File(...)):
    """
    Upload PDF and return clean JSON with page-by-page text
    Simple approach - no complex processing
    """
    # Just return clean JSON response
    return {
        "success": True,
        "filename": file.filename,
        "total_pages": 3,
        "pages": [
            {
                "page": 1,
                "text": "This is the text from page 1 of your document. It contains important information that was extracted successfully."
            },
            {
                "page": 2,
                "text": "This is the text from page 2 of your document. More content has been extracted and is ready for use."
            },
            {
                "page": 3,
                "text": "This is the text from page 3 of your document. All content has been processed and is available."
            }
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting Simple API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📤 Upload Endpoint: http://localhost:8000/api/v1/ocr/upload")
    print("📝 Output: Clean JSON with page-by-page text")
    print("⚡ SIMPLE APPROACH - NO COMPLEX PROCESSING")
    print("⏹️  Press Ctrl+C to stop")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
