import os
import shutil
import base64
import json
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.database import ImageCatalog, Base

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(ROOT_DIR, "curated_catalog")
STATIC_CATALOG_DIR = os.path.join(ROOT_DIR, "static", "catalog")

client = OpenAI(api_key=OPENAI_API_KEY)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def init_db():
    print("Connecting to database...")
    engine = create_engine(str(DATABASE_URL))
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()

def generate_image_metadata(image_path):
    print(f"Analyzing {os.path.basename(image_path)} with gpt-4o-mini...")
    base64_image = encode_image(image_path)
    
    prompt = """
    Analyze this interior design photo. Provide a JSON object with:
    1. 'room_type': the type of room (e.g. living_room, bedroom, kitchen, bathroom)
    2. 'style': the overarching design style (e.g. modern, minimalist, boho, industrial, scandinavian, organic_modern, midcentury)
    3. 'description': A rich, highly detailed paragraph describing the aesthetics, colors, textures, lighting, and mood.
    Return ONLY valid JSON.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ],
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=300
    )
    
    return json.loads(response.choices[0].message.content or "{}")

def generate_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def seed_catalog():
    if not os.path.exists(SOURCE_DIR):
        print(f"Creating source directory {SOURCE_DIR}")
        os.makedirs(SOURCE_DIR)
        print("Please place your images in this folder and run the script again.")
        return
        
    os.makedirs(STATIC_CATALOG_DIR, exist_ok=True)
    
    session = init_db()
    
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    
    images_processed = 0
    
    for filename in os.listdir(SOURCE_DIR):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in valid_extensions:
            continue
            
        source_path = os.path.join(SOURCE_DIR, filename)
        dest_filename = filename.replace(" ", "_").lower()
        dest_path = os.path.join(STATIC_CATALOG_DIR, dest_filename)
        
        # Check if already processed
        url_path = f"/static/catalog/{dest_filename}"
        existing = session.query(ImageCatalog).filter_by(image_url=url_path).first()
        if existing:
            print(f"Skipping {filename}, already in database.")
            continue
            
        # Copy to static folder so frontend can serve it
        shutil.copy2(source_path, dest_path)
        
        try:
            # 1. Vision Analysis (using gpt-4o-mini to save cost!)
            metadata = generate_image_metadata(source_path)
            
            # 2. Vector Embedding (using text-embedding-3-small)
            embedding = generate_embedding(metadata["description"])
            
            # 3. Save to DB
            new_concept = ImageCatalog(
                image_url=url_path,
                description=metadata["description"],
                room_type=metadata.get("room_type", "unknown").replace(" ", "_").lower(),
                style=metadata.get("style", "unknown").lower(),
                embedding=embedding
            )
            
            session.add(new_concept)
            session.commit()
            print(f"Successfully added {filename} to RAG catalog.")
            images_processed += 1
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            session.rollback()
            
    print(f"\\nSeeding complete. Processed {images_processed} new images.")

if __name__ == "__main__":
    seed_catalog()
