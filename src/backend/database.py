import json
from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column
from src.backend.config import DATABASE_URL

# Create database engine and session
# SQLite requires check_same_thread=False, but PostgreSQL will crash if you pass it!
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Project Parameters
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    room_type: Mapped[str | None] = mapped_column(String, nullable=True)
    area_sqft: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scope_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    material_tier: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Financial Estimates
    # (Budget fields removed in favor of Sourcing List)
    
    # Readiness Metrics
    readiness_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    timeline: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Multi-Modal Vision Analysis (JSON encoded string)
    vision_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Taste Profile & Generative Sourcing
    style_answers: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected_image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    design_dna: Mapped[str | None] = mapped_column(String, nullable=True)
    sourcing_list: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Lead Status & Outputs
    status: Mapped[str] = mapped_column(String, default="New")
    pdf_path: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

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
            "readiness_score": self.readiness_score,
            "timeline": self.timeline,
            "vision_analysis": json.loads(self.vision_analysis) if isinstance(self.vision_analysis, str) else None,
            "style_answers": json.loads(self.style_answers) if isinstance(self.style_answers, str) else None,
            "selected_image_url": self.selected_image_url,
            "design_dna": self.design_dna,
            "sourcing_list": json.loads(self.sourcing_list) if isinstance(self.sourcing_list, str) else None,
            "status": self.status,
            "pdf_path": self.pdf_path,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    message: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String, default="Feedback")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "message": self.message,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

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
