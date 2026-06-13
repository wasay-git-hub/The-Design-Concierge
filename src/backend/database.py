import json
from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column
from src.backend.config import DATABASE_URL

# Create database engine and session
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # check_same_thread=False is needed for SQLite multi-threading
)
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
    decision_maker: Mapped[str | None] = mapped_column(String, nullable=True)
    
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
        if self.area_sqft is not None and self.scope_level is not None and self.material_tier is not None:
            from src.backend.model_pipeline.model import predict_design_cost
            try:
                budget_min, budget_max = predict_design_cost(
                    location=self.location or "Austin",
                    room_type=self.room_type or "Living Room",
                    area_sqft=self.area_sqft,
                    scope_level=self.scope_level,
                    material_tier=self.material_tier
                )
            except Exception:
                budget_min, budget_max = None, None
        else:
            budget_min, budget_max = None, None

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
            "budget_min": budget_min,
            "budget_max": budget_max,
            "readiness_score": self.readiness_score,
            "timeline": self.timeline,
            "decision_maker": self.decision_maker,
            "vision_analysis": json.loads(self.vision_analysis) if isinstance(self.vision_analysis, str) else None,
            "style_answers": json.loads(self.style_answers) if isinstance(self.style_answers, str) else None,
            "selected_image_url": self.selected_image_url,
            "design_dna": self.design_dna,
            "sourcing_list": json.loads(self.sourcing_list) if isinstance(self.sourcing_list, str) else None,
            "status": self.status,
            "pdf_path": self.pdf_path,
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
