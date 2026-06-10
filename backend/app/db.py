import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.config import DATABASE_URL

# Create database engine and session
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # check_same_thread=False is needed for SQLite multi-threading
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    
    # Project Parameters
    location = Column(String, nullable=True)
    room_type = Column(String, nullable=True)
    area_sqft = Column(Integer, nullable=True)
    scope_level = Column(Integer, nullable=True)
    material_tier = Column(Integer, nullable=True)
    
    # Financial Estimates
    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)
    
    # Readiness Metrics
    readiness_score = Column(Integer, nullable=True)
    timeline = Column(String, nullable=True)
    decision_maker = Column(String, nullable=True)
    
    # Multi-Modal Vision Analysis (JSON encoded string)
    vision_analysis = Column(Text, nullable=True)
    
    # Taste Profile
    design_dna = Column(String, nullable=True)
    
    # Lead Status & Outputs
    status = Column(String, default="New")
    pdf_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "location": self.location,
            "room_type": self.room_type,
            "area_sqft": self.area_sqft,
            "scope_level": self.scope_level,
            "material_tier": self.material_tier,
            "budget_min": self.budget_min,
            "budget_max": self.budget_max,
            "readiness_score": self.readiness_score,
            "timeline": self.timeline,
            "decision_maker": self.decision_maker,
            "vision_analysis": json.loads(self.vision_analysis) if self.vision_analysis else None,
            "design_dna": self.design_dna,
            "status": self.status,
            "pdf_path": self.pdf_path,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ConversationState(Base):
    __tablename__ = "conversation_states"

    lead_id = Column(String, primary_key=True, index=True)
    graph_state = Column(Text, nullable=True)  # Serialized JSON representation of LangGraph state
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database dependency helper
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")
