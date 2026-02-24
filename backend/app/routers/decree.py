from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.ocr_service import process_document
from app.services.embedding_service import get_embedding
from app.services.vector_store import add_decree_article
import shutil
import os

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_decree(file: UploadFile = File(...)):
    print(f"Received Decree: {file.filename}")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # 1. Save File
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. OCR and Split
        print("Starting OCR processing for Decree...")
        ocr_result = process_document(file_path)
        articles = ocr_result.get("articles", [])
        
        if not articles:
            return {"message": "No articles found in decree.", "filename": file.filename}

        # 3. Embed and Store
        print(f"Embedding {len(articles)} articles...")
        count = 0
        for article in articles:
            text = article["content"]
            number = article["article_number"]
            
            if text and len(text) > 10: # Skip empty or very short chunks
                embedding = get_embedding(text)
                add_decree_article(text, number, file.filename, embedding)
                count += 1
                
        return {
            "filename": file.filename,
            "message": f"Decree processed successfully.",
            "articles_stored": count
        }
        
    except Exception as e:
        print(f"Error processing decree: {e}")
        raise HTTPException(status_code=500, detail=str(e))
