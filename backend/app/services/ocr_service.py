import os
import pytesseract
import re
from pdf2image import convert_from_path
from PIL import Image

def extract_text_from_pdf(file_path: str) -> str:
    try:
        print(f"Processing document: {file_path}")
        images = convert_from_path(file_path)
        
        full_text = ""
        for i, image in enumerate(images):
            print(f"  - OCR Page {i+1}...")
            text = pytesseract.image_to_string(image, lang='fra')
            full_text += f"\n--- Page {i+1} ---\n{text}"
            
        return full_text
    except Exception as e:
        print(f"OCR Error: {e}")
        if "poppler" in str(e).lower():
            print("TIP: Poppler is required for PDF-to-image conversion. On Windows, install it and add the /bin folder to your PATH.")
        return ""

def split_into_articles(text: str) -> list[dict]:
    # Improved regex to catch "Article 1", "ARTICLE 1", "Art. 1", "Article premier"
    article_pattern = re.compile(r'(?i)^\s*(?:Article|ART)\.?\s*(\d+|premier|[IVX]+)', re.MULTILINE)
    
    articles = []
    matches = list(article_pattern.finditer(text))
    
    if not matches:
        return [{"article_number": "N/A", "content": text}]
    
    for i, match in enumerate(matches):
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(text)
        article_num = match.group(1)
        content = text[match.end():end_idx].strip()
        
        # Clean up content
        content = re.sub(r'\n+', ' ', content) # Replace newlines with spaces
        
        articles.append({
            "article_number": article_num,
            "content": content
        })
        
    print(f"Split document into {len(articles)} articles.")
    return articles

def process_document(file_path: str):
    raw_text = extract_text_from_pdf(file_path)
    articles = split_into_articles(raw_text)
    
    return {
        "raw_text": raw_text,
        "articles": articles,
        "page_count": 0
    }
