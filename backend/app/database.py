import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_pg_connection():
    """Returns a connection object for PostgreSQL."""
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "db"),
        database=os.getenv("PG_DB", "cpslyse_db"),
        user=os.getenv("PG_USER", "user_admin"),
        password=os.getenv("PG_PASSWORD", "password123")
    )

def init_db():
    """Initializes the database schema for legal RAG analysis."""
    retries = 5
    while retries > 0:
        try:
            conn = get_pg_connection()
            cur = conn.cursor()
            
            # --- 1. ENABLE VECTOR EXTENSION ---
            # This is mandatory for storing AI embeddings
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # --- 2. DECREE REFERENCE TABLE (The Law) ---
            # We store the 'Decret' here. It acts as the benchmark.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS decret_reference (
                    id SERIAL PRIMARY KEY,
                    article_title VARCHAR(255),
                    content TEXT NOT NULL,
                    embedding vector(384) -- 384 matches local models like all-MiniLM-L6-v2
                );
            """)

            # --- 3. CPS ARTICLES TABLE (The Uploaded Document) ---
            # We store the Tesseract output here, split by article.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cps_articles (
                    id SERIAL PRIMARY KEY,
                    filename TEXT,
                    article_number VARCHAR(100),
                    content TEXT NOT NULL,
                    page_number INT,
                    embedding vector(384),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # --- 4. GAP ANALYSIS RESULTS (The AI Findings) ---
            # This stores Step 5: Keywords/clauses missing or illegal.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS legal_mismatches (
                    id SERIAL PRIMARY KEY,
                    cps_article_id INT REFERENCES cps_articles(id) ON DELETE CASCADE,
                    decret_article_id INT REFERENCES decret_reference(id),
                    issue_type VARCHAR(50), -- e.g., 'Contradiction', 'Omission', 'Keyword'
                    detected_keyword VARCHAR(255),
                    description TEXT,        -- The AI's explanation
                    severity VARCHAR(20) DEFAULT 'Warning'
                );
            """)

            conn.commit()
            cur.close()
            conn.close()
            print("✅ Database initialized with Vector support.")
            break
            
        except Exception as e:
            print(f"🔄 Waiting for Database... ({e})")
            retries -= 1
            time.sleep(3)

if __name__ == "__main__":
    init_db()