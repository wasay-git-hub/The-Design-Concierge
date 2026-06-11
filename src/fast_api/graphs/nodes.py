import os
import json
import base64
import re
from typing import Dict, Any, List
from openai import OpenAI
from src.fast_api.config import OPENAI_API_KEY
from src.model_pipeline.model import predict_design_cost

def get_openai_client():
    if OPENAI_API_KEY:
        return OpenAI(api_key=OPENAI_API_KEY)
    return None

def encode_image(image_path: str) -> str:
    """Encodes a local file image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_room_photo_with_gpt4o(image_path: str) -> Dict[str, Any]:
    """
    Sends the uploaded photo to the GPT-4o Vision API to analyze room aesthetics,
    architectural bones, lighting, and layout constraints.
    """
    client = get_openai_client()
    if not client:
        raise ValueError("OpenAI API key is missing or invalid.")

    try:
        base64_image = encode_image(image_path)
        
        prompt = """
        You are a Senior Technical Architect and Principal Interior Designer. 
        Analyze this room photo and output a highly detailed, professional analysis in JSON format.
        Focus on structural elements, lighting limits, styling details, and design challenges.
        
        Your output JSON must contain exactly these keys:
        - "architectural_bones": String. Describe structure (moldings, ceiling height, fireplace, column locations).
        - "lighting_profile": String. Describe natural light direction and sources vs. artificial light issues.
        - "current_style": String. Identify current layout theme and colors.
        - "estimated_dimensions": String. Estimate height, width, length, and square footage.
        - "potential_pain_points": String. Space plan leaks, light blocks, awkward corners.
        - "mismatch_triggers": List of strings. Underwear style keywords that clash with these architectural bones (e.g. 'industrial' if there are ornate Victorian details).
        
        Respond ONLY with the raw JSON string. Do not include markdown code block syntax.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI vision response content is empty.")
        result = json.loads(content)
        return result
    except Exception as e:
        raise RuntimeError(f"GPT-4o Vision API call failed: {e}")

def node_welcome(state: Dict[str, Any]) -> Dict[str, Any]:
    """Phase 1: Welcome & Initial Greetings"""
    chat_history = state.get("chat_history", [])
    
    welcome_msg = (
        "Welcome to The Design Concierge. I am your Digital Junior Designer. "
        "Before we begin crafting your space's design dna, I would love to examine the room. "
        "Please upload a photo of the current state of your room and tell me its general layout!"
    )
    
    if not chat_history:
        chat_history.append({"role": "assistant", "content": welcome_msg})
        
    return {
        "chat_history": chat_history,
        "next_node": "vision_analysis",
        "current_question": "Please upload a photo of your room to proceed.",
        "is_complete": False
    }

def node_vision_analysis(state: Dict[str, Any]) -> Dict[str, Any]:
    """Phase 2: Photo upload and Vision Analysis"""
    chat_history = state.get("chat_history", [])
    image_path = state.get("room_photo_url")
    
    if not image_path or not os.path.exists(image_path):
        return {
            "next_node": "vision_analysis",
            "current_question": "I need you to upload a room photo before we can move on."
        }
        
    # Analyze the photo
    print(f"Analyzing room image: '{image_path}'...")
    try:
        vision_profile = analyze_room_photo_with_gpt4o(image_path)
    except Exception as e:
        error_msg = f"I'm sorry, I encountered a technical error while analyzing the photo: {str(e)}"
        chat_history.append({"role": "assistant", "content": error_msg})
        return {
            "chat_history": chat_history,
            "next_node": "vision_analysis",
            "current_question": "Please check the API configuration and try uploading again."
        }
    
    response_msg = (
        f"Thank you for sharing your space. I've analyzed your photo, and here is what I see:\n\n"
        f"🏛️ **Architectural Bones:** {vision_profile['architectural_bones']}\n\n"
        f"☀️ **Lighting Profile:** {vision_profile['lighting_profile']}\n\n"
        f"🎨 **Current Aesthetic:** {vision_profile['current_style']}\n\n"
        f"I've got the structural constraints logged. Now, tell me: what is your dream style or vision for this room? "
        "Are there any specific materials or must-haves you are imagining?"
    )
    
    chat_history.append({"role": "assistant", "content": response_msg})
    
    return {
        "vision_analysis": vision_profile,
        "chat_history": chat_history,
        "next_node": "visual_taste_test",
        "current_question": "What is your dream style or design vision for this room?",
        "is_complete": False
    }

def node_visual_taste_test(state: Dict[str, Any]) -> Dict[str, Any]:
    """Phase 2.5: Present visual taste test options to the user"""
    chat_history = state.get("chat_history", [])
    
    visual_options = [
        {"id": "organic_modern", "label": "Organic Modern", "url": "/static/styles/organic_modern.png"},
        {"id": "scandinavian_minimalist", "label": "Scandinavian Minimalist", "url": "/static/styles/scandinavian_minimalist.png"},
        {"id": "art_deco", "label": "Art Deco Luxury", "url": "/static/styles/art_deco.png"},
        {"id": "industrial_chic", "label": "Industrial Chic", "url": "/static/styles/industrial_chic.png"}
    ]
    
    response_msg = "To ensure I understand your aesthetic, please select the design style below that most closely aligns with your vision for the space:"
    
    chat_history.append({
        "role": "assistant", 
        "content": response_msg,
        "visual_options": visual_options
    })
    
    return {
        "chat_history": chat_history,
        "next_node": "refinement",
        "current_question": "Please select a design style from the images provided.",
        "is_complete": False
    }

def node_refinement(state: Dict[str, Any]) -> Dict[str, Any]:
    """Phase 3: Refine the vision, detect conflicts and ask style DNA questions"""
    chat_history = state.get("chat_history", [])
    vision_analysis = state.get("vision_analysis", {})
    user_input = chat_history[-1]["content"] if chat_history and chat_history[-1]["role"] == "user" else ""
    preferred_visual_style = state.get("preferred_visual_style", "")
    
    # Explicitly catch and store the visual taste test selection
    if "I select the " in user_input and " style." in user_input:
        match = re.search(r"I select the (.*) style\.", user_input)
        if match:
            preferred_visual_style = match.group(1)
    
    client = get_openai_client()
    
    # Check if we have collected enough design details
    # We want at least a target style, budget willingness, timeline, and decision-maker status.
    # We query an LLM to check if these criteria are met.
    # The output JSON format contains is_sufficient, next_question, design_dna, timeline, etc.

    prompt = f"""
    You are a Senior Design Assistant. Review the conversation history and project details:
    Vision Profile: {json.dumps(vision_analysis)}
    Preferred Visual Style: {preferred_visual_style if preferred_visual_style else 'None selected'}
    Conversation History: {json.dumps(chat_history[-6:])}
    
    We need to identify:
    1. Client's target Design Style (e.g. Organic Modern, Japandi, Art Deco, etc.). Ensure it aligns with their Preferred Visual Style if one is selected.
    2. Estimated room size (area_sqft), scope of work (furnishing, soft remodel, gut renovation), and material tier (premium, luxury, ultra-luxury)
    3. Project Timeline (immediate, 3-6 months, flexible)
    4. Decision maker status (who is the final decision maker)
    
    If any of these details are missing, return a JSON with:
    "is_sufficient": false,
    "next_question": "Your highly customized, warm, design-focused question to prompt the client for the missing detail. If there is a style-structure mismatch (e.g., they want a Scandinavian light wood aesthetic, but the Vision Profile reveals a dark, windowless basement room), gently explain the structural friction and suggest a creative designer workaround (e.g., using light plaster wall textures and high-CRI layered lighting) and ask if they are open to it."
    
    If all details are present, return a JSON with:
    "is_sufficient": true,
    "design_dna": "The final consolidated style name",
    "timeline": "Timeline summary",
    "decision_maker": "Decision-maker summary",
    "area_sqft": Int (estimate if not explicitly given, e.g. 300),
    "scope_level": Int (1 = Furnishing, 2 = Soft Remodel, 3 = Gut Renovate),
    "material_tier": Int (1 = Premium, 2 = Luxury, 3 = Ultra-Luxury)
    
    Ensure your response is ONLY valid JSON.
    """

    if not client:
        error_msg = "I'm sorry, I encountered a technical error: OpenAI API key is missing or invalid."
        chat_history.append({"role": "assistant", "content": error_msg})
        return {
            "chat_history": chat_history,
            "next_node": "refinement",
            "current_question": "Please check the API configuration and try again."
        }
            
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI refinement response content is empty.")
        res = json.loads(content)
        
        if res.get("is_sufficient"):
            return {
                "preferred_visual_style": preferred_visual_style,
                "design_dna": res.get("design_dna", "Modern Luxury"),
                "timeline": res.get("timeline", "Flexible"),
                "decision_maker": res.get("decision_maker", "Owner"),
                "area_sqft": int(res.get("area_sqft", 300)),
                "scope_level": int(res.get("scope_level", 2)),
                "material_tier": int(res.get("material_tier", 2)),
                "next_node": "synthesis",
                "is_complete": True
            }
        else:
            q = res.get("next_question", "Could you tell me more about your timeline and expectations?")
            chat_history.append({"role": "assistant", "content": q})
            return {
                "preferred_visual_style": preferred_visual_style,
                "chat_history": chat_history,
                "next_node": "refinement",
                "current_question": q,
                "is_complete": False
            }
    except Exception as e:
        error_msg = f"I'm sorry, I encountered a technical error while processing your response: {str(e)}"
        chat_history.append({"role": "assistant", "content": error_msg})
        return {
            "preferred_visual_style": preferred_visual_style,
            "chat_history": chat_history,
            "next_node": "refinement",
            "current_question": "Please try again once the issue is resolved."
        }

def node_synthesis(state: Dict[str, Any]) -> Dict[str, Any]:
    """Phase 4: Synthesis, budget estimation, readiness scoring"""
    # 1. Run ML Budget Prediction
    location = state.get("location", "Austin")
    room_type = state.get("room_type", "Living Room")
    area_sqft = state.get("area_sqft", 300)
    scope_level = state.get("scope_level", 2)
    material_tier = state.get("material_tier", 2)
    
    # ML Prediction range
    budget_min, budget_max = predict_design_cost(
        location=location,
        room_type=room_type,
        area_sqft=area_sqft,
        scope_level=scope_level,
        material_tier=material_tier
    )
    
    # 2. Compute Readiness Score (0-100)
    # Timeline score: immediate (20), 3-6 months (20), flexible (15), rush (5)
    timeline_str = state.get("timeline", "3-6 months").lower()
    t_score = 20
    if "immediate" in timeline_str or "3-6" in timeline_str:
        t_score = 20
    elif "flex" in timeline_str:
        t_score = 15
    elif "rush" in timeline_str or "week" in timeline_str:
        t_score = 10
        
    # Decision Maker: all parties aligned (20), solo (15), unaligned (5)
    dm_str = state.get("decision_maker", "Solo").lower()
    dm_score = 20
    if "partner" in dm_str or "spouse" in dm_str or "both" in dm_str:
        dm_score = 20
    elif "solo" in dm_str or "self" in dm_str:
        dm_score = 15
        
    # Scope Clarity: room dimensions & vision available (20)
    scope_score = 20 if state.get("vision_analysis") else 10
    
    # Budget Comfort: If they complete onboarding, we award budget points (40)
    # We will adjust this if they indicate budget alignment in final report view
    b_score = 40 
    
    readiness_score = t_score + dm_score + scope_score + b_score
    
    summary_msg = (
        f"Thank you for completing the Taste Discovery process. "
        f"I have compiled your Project Design Brief.\n\n"
        f"📊 **Design DNA:** {state.get('design_dna', 'Custom Classic')}\n"
        f"📏 **Estimated Space Area:** {area_sqft} sq ft\n"
        f"💵 **ML Estimated Budget Range:** ${budget_min:,.2f} - ${budget_max:,.2f}\n"
        f"📋 **Project Readiness Score:** {readiness_score}/100\n\n"
        f"I am compiling this information into a Project Intelligence Report for your Architect/Designer. "
        f"They will reach out to schedule your 1-on-1 design consultation."
    )
    
    chat_history = state.get("chat_history", [])
    chat_history.append({"role": "assistant", "content": summary_msg})
    
    return {
        "budget_min": budget_min,
        "budget_max": budget_max,
        "readiness_score": readiness_score,
        "chat_history": chat_history,
        "is_complete": True,
        "next_node": "END"
    }
