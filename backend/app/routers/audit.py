from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.ocr_service import process_document
from app.database import get_db
import shutil
import os
from datetime import datetime

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/")
def get_audit():
    return {"message": "Audit service is running"}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    print(f"Received file: {file.filename}")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print("Starting OCR processing...")
        ocr_result = process_document(file_path)
        
        print("Saving to MongoDB...")
        db = get_db()
        
        document_entry = {
            "filename": file.filename,
            "uploaded_at": datetime.utcnow(),
            "status": "processed",
            "raw_text": ocr_result.get("raw_text", "")
        }
        doc_result = db.documents.insert_one(document_entry)
        doc_id = doc_result.inserted_id
        
        articles = ocr_result.get("articles", [])
        if articles:
            for art in articles:
                art["document_id"] = doc_id
                art["filename"] = file.filename
                db.articles.insert_one(art)
        
        # Prepare articles for response (convert ObjectIds to strings and remove internal ID)
        response_articles = []
        for art in articles:
            serializable_art = {k: v for k, v in art.items() if k != '_id'}
            serializable_art["document_id"] = str(doc_id)
            response_articles.append(serializable_art)
                
        return {
            "filename": file.filename, 
            "message": f"File processed. {len(articles)} articles extracted.", 
            "id": str(doc_id),
            "articles": response_articles
        }
        
    except Exception as e:
        print(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
