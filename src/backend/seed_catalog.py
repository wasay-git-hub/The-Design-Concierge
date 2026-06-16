import os
import shutil
import base64
import json
from dotenv import load_dotenv
from langfuse.openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.database import ImageCatalog, Base

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(ROOT_DIR))
CATALOG_DIR = os.path.join(PROJECT_ROOT, "static", "catalog")

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
    if not os.path.exists(CATALOG_DIR):
        print(f"Directory not found: {CATALOG_DIR}")
        return
        
    session = init_db()
    
    images_processed = 0
    
    for filename in os.listdir(CATALOG_DIR):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            continue

        file_path = os.path.join(CATALOG_DIR, filename)
        
        # Check if already processed
        url_path = f"/static/catalog/{filename}"
        existing = session.query(ImageCatalog).filter_by(image_url=url_path).first()
        if existing:
            print(f"Skipping {filename}, already in database.")
            continue
            
        # 1. Analyze with GPT-4o-mini Vision
        try:
            print(f"Analyzing {filename} with gpt-4o-mini...")
            vision_result = generate_image_metadata(file_path)
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")
            continue

        # 2. Generate Vector Embedding
        combined_text = (
            f"room_type: {vision_result['room_type']} "
            f"style: {vision_result['style']} "
            f"description: {vision_result['description']}"
        )
        try:
            vector_embedding = generate_embedding(combined_text)
        except Exception as e:
            print(f"Error generating embedding for {filename}: {e}")
            continue

        # 3. Save to Database
        try:
            new_entry = ImageCatalog(
                image_url=url_path,
                description=vision_result["description"],
                room_type=vision_result.get("room_type", "unknown").replace(" ", "_").lower(),
                style=vision_result.get("style", "unknown").lower(),
                embedding=vector_embedding
            )
            
            session.add(new_entry)
            session.commit()
            print(f"Successfully added {filename} to RAG catalog.")
            images_processed += 1
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            session.rollback()
            
    print(f"\\nSeeding complete. Processed {images_processed} new images.")

if __name__ == "__main__":
    seed_catalog()
