import os
import json
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from src.backend.config import UPLOAD_DIR
from src.backend.database import get_db, init_db, Lead
from src.backend.graphs.workflow import compiled_graph
from src.backend.utils.pdf_generator import generate_intelligence_report

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="The Design Concierge API", lifespan=lifespan)

# Configure CORS for Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify next.js dev port e.g. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded photos and generated PDF reports static files
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
static_dir = os.path.join(root_dir, "static")
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
    
    # Run the graph: It will start at 'welcome' and stop before 'vision_analysis'
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
    
    config = {"configurable": {"thread_id": lead_id}}
    state_result = compiled_graph.invoke(initial_state, config)
    
    db.commit()
    
    return {
        "lead_id": lead_id,
        "chat_history": state_result["chat_history"],
        "current_question": state_result["current_question"],
        "next_node": state_result["next_node"]
    }

@app.post("/api/upload-photo")
def upload_room_photo(
    lead_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Step 2: Upload room photo, save it locally, and run Vision Analysis node.
    """
    # 1. Fetch lead
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead session not found.")
        
    # 2. Save photo file to static folder
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename.")
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{lead_id}_room{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
        
    # 3. Update LangGraph State with the photo path
    config = {"configurable": {"thread_id": lead_id}}
    compiled_graph.update_state(config, {"room_photo_url": file_path})
    
    # 4. Invoke the graph (Resumes from vision_analysis breakpoint, flows through visual_taste_test, stops at refinement)
    state = compiled_graph.invoke(None, config)
    
    if state.get("next_node") == "vision_analysis":
        error_msg = state.get("current_question", "Failed to analyze image. Please try again.")
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Save structured vision results to database
    if "vision_analysis" in state and state["vision_analysis"]:
        lead.vision_analysis = json.dumps(state["vision_analysis"])
    
    db.commit()
    
    return {
        "chat_history": state["chat_history"],
        "vision_analysis": state.get("vision_analysis", {}),
        "current_question": state.get("current_question", ""),
        "next_node": state.get("next_node", "")
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
    # 1. Fetch lead
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead session not found.")
        
    config = {"configurable": {"thread_id": lead_id}}
    current_state = compiled_graph.get_state(config).values
    
    # 2. Append user response to state history
    chat_history = current_state.get("chat_history", [])
    chat_history.append({"role": "user", "content": message})
    compiled_graph.update_state(config, {"chat_history": chat_history})
    
    # 3. Invoke graph to resume from refinement
    state = compiled_graph.invoke(None, config)
    
    # 4. Check if refinement is complete
    if state.get("is_complete"):
        # Sync Lead model columns with finalized assessment values
        lead.design_dna = state.get("design_dna")
        lead.area_sqft = state.get("area_sqft")
        lead.scope_level = state.get("scope_level")
        lead.material_tier = state.get("material_tier")
        lead.timeline = state.get("timeline")
        lead.readiness_score = state.get("readiness_score")
        lead.style_answers = json.dumps(state.get("style_answers", {}))
        lead.selected_image_url = state.get("selected_image_url")
        lead.sourcing_list = json.dumps(state.get("sourcing_list", []))
        lead.status = "Assessed"
        
    db.commit()
    
    lead_dict = lead.to_dict() if state.get("is_complete") else {}
    
    return {
        "chat_history": state["chat_history"],
        "next_node": state.get("next_node", ""),
        "current_question": state.get("current_question", ""),
        "is_complete": state.get("is_complete", False),
        "lead_summary": {
            "design_dna": lead.design_dna,
            "readiness_score": lead.readiness_score,
            "sourcing_list": state.get("sourcing_list", [])
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
    pdf_path = generate_intelligence_report(lead_dict, output_dir=os.path.join(static_dir, "reports"))
    
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
