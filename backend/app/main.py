import os
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.app.config import UPLOAD_DIR
from backend.app.db import get_db, init_db, Lead, ConversationState
from backend.app.ml.model import predict_design_cost
from backend.app.graphs.nodes import (
    node_welcome,
    node_vision_analysis,
    node_refinement,
    node_synthesis
)
from backend.app.utils.pdf_generator import generate_intelligence_report

app = FastAPI(title="The Design Concierge API")

# Configure CORS for Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify next.js dev port e.g. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Serve uploaded photos and generated PDF reports static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(os.path.join(static_dir, "reports"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.post("/api/onboard")
def onboard_client(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    location: str = Form(...),
    room_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Step 1: Initialize lead profile and start the conversation.
    """
    lead_id = str(uuid.uuid4())
    
    # Create Lead database entry
    new_lead = Lead(
        id=lead_id,
        name=name,
        email=email,
        phone=phone,
        location=location,
        room_type=room_type,
        status="Onboarding"
    )
    db.add(new_lead)
    
    # Run welcome state node to get the initial assistant greeting
    initial_state = {
        "client_id": lead_id,
        "name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "room_type": room_type,
        "chat_history": [],
        "next_node": "welcome",
        "is_complete": False
    }
    
    welcome_result = node_welcome(initial_state)
    initial_state.update(welcome_result)
    
    # Save conversation state in DB
    conv_state = ConversationState(
        lead_id=lead_id,
        graph_state=json.dumps(initial_state)
    )
    db.add(conv_state)
    db.commit()
    
    return {
        "lead_id": lead_id,
        "chat_history": initial_state["chat_history"],
        "current_question": initial_state["current_question"],
        "next_node": initial_state["next_node"]
    }

@app.post("/api/upload-photo")
async def upload_room_photo(
    lead_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Step 2: Upload room photo, save it locally, and run Vision Analysis node.
    """
    # 1. Fetch lead and conversation state
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    conv = db.query(ConversationState).filter(ConversationState.lead_id == lead_id).first()
    
    if not lead or not conv:
        raise HTTPException(status_code=404, detail="Lead session not found.")
        
    state = json.loads(conv.graph_state)
    
    # 2. Save photo file to static folder
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{lead_id}_room{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    # Relative path for serving via web server
    relative_photo_url = f"static/uploads/{safe_filename}"
    state["room_photo_url"] = file_path # Absolute local path for OpenCV / OpenAI processing
    
    # 3. Execute Vision analysis node
    analysis_result = node_vision_analysis(state)
    state.update(analysis_result)
    
    # Save structured vision results to database
    lead.vision_analysis = json.dumps(state["vision_analysis"])
    
    # Save conversation progress
    conv.graph_state = json.dumps(state)
    db.commit()
    
    return {
        "chat_history": state["chat_history"],
        "vision_analysis": state["vision_analysis"],
        "current_question": state["current_question"],
        "next_node": state["next_node"]
    }

@app.post("/api/chat")
def chat_refinement(
    lead_id: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Step 3: Handle taste discovery chat and resolve design-reality friction.
    """
    # 1. Load conversation state
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    conv = db.query(ConversationState).filter(ConversationState.lead_id == lead_id).first()
    
    if not lead or not conv:
        raise HTTPException(status_code=404, detail="Lead session not found.")
        
    state = json.loads(conv.graph_state)
    
    # 2. Append user response to state history
    state["chat_history"].append({"role": "user", "content": message})
    
    # 3. Execute refinement node
    refinement_result = node_refinement(state)
    state.update(refinement_result)
    
    # 4. If refinement indicates state is sufficient, run synthesis immediately
    if state.get("is_complete") or state.get("next_node") == "synthesis":
        synthesis_result = node_synthesis(state)
        state.update(synthesis_result)
        
        # Sync Lead model columns with finalized assessment values
        lead.design_dna = state.get("design_dna")
        lead.area_sqft = state.get("area_sqft")
        lead.scope_level = state.get("scope_level")
        lead.material_tier = state.get("material_tier")
        lead.timeline = state.get("timeline")
        lead.decision_maker = state.get("decision_maker")
        lead.budget_min = state.get("budget_min")
        lead.budget_max = state.get("budget_max")
        lead.readiness_score = state.get("readiness_score")
        lead.status = "Assessed"
        
    # Save conversation state progress
    conv.graph_state = json.dumps(state)
    db.commit()
    
    return {
        "chat_history": state["chat_history"],
        "next_node": state["next_node"],
        "current_question": state.get("current_question", ""),
        "is_complete": state.get("is_complete", False),
        "lead_summary": {
            "design_dna": lead.design_dna,
            "budget_min": lead.budget_min,
            "budget_max": lead.budget_max,
            "readiness_score": lead.readiness_score
        } if state.get("is_complete") else None
    }

@app.post("/api/generate-report")
def generate_report(
    lead_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Step 4: finalizes the project profile, compiles the ReportLab PDF and returns the URL.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
        
    lead_dict = lead.to_dict()
    
    # Execute ReportLab PDF layout generator
    print(f"Generating PDF Intelligence Report for: {lead.name}...")
    pdf_path = generate_intelligence_report(lead_dict)
    
    # Store path to PDF in the database
    lead.pdf_path = pdf_path
    lead.status = "Report Generated"
    db.commit()
    
    return {
        "success": True,
        "pdf_url": f"/static/reports/report_{lead_id}.pdf",
        "lead": lead.to_dict()
    }

@app.get("/api/leads")
def get_all_leads(db: Session = Depends(get_db)):
    """
    Designer Portal Dashboard Lead List
    """
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    return [l.to_dict() for l in leads]

@app.get("/api/leads/{lead_id}")
def get_lead_details(lead_id: str, db: Session = Depends(get_db)):
    """
    Designer Portal Lead Detail View
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    return lead.to_dict()
