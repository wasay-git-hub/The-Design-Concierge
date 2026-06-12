import os
import json
import base64
import re
import random
import pandas as pd
from typing import Dict, Any, List
from openai import OpenAI
from src.backend.config import OPENAI_API_KEY

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
            model="gpt-5.4-mini",
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
        f"I've got the structural constraints logged. Now, let's nail down your specific taste."
    )
    
    chat_history.append({"role": "assistant", "content": response_msg})
    
    return {
        "vision_analysis": vision_profile,
        "chat_history": chat_history,
        "next_node": "style_questionnaire",
        "current_question": "Let's begin the taste discovery.",
        "is_complete": False
    }

def node_style_questionnaire(state: Dict[str, Any]) -> Dict[str, Any]:
    """Phase 2.5: Ask 4 style questions to build the dynamic query profile"""
    chat_history = state.get("chat_history", [])
    style_answers = state.get("style_answers", {})
    if not style_answers:
        style_answers = {}
        
    QUESTIONS = [
        {"key": "atmosphere", "q": "Do you lean toward light, airy, and bright spaces, or dark, moody, and cozy environments?"},
        {"key": "lighting", "q": "When you imagine the lighting, do you prefer crisp white daylight, or warm, golden, amber glows?"},
        {"key": "texture", "q": "Do you prefer sleek, polished, and modern surfaces (glass, metal, marble), or raw, organic, and textured elements (raw wood, linen, stone)?"},
        {"key": "energy", "q": "Should the room feel perfectly minimalist and uncluttered, or layered, collected, and full of character?"}
    ]
    
    client = get_openai_client()
    
    # Process the last user message to extract answer if available
    if len(chat_history) > 0 and chat_history[-1]["role"] == "user" and len(style_answers) < len(QUESTIONS):
        # We need to determine which question they answered. It's usually the first one that is missing.
        missing_keys = [item["key"] for item in QUESTIONS if item["key"] not in style_answers]
        current_q_key = missing_keys[0] if missing_keys else None
        
        if current_q_key and client:
            try:
                prompt = f"The user replied to a design question. Extract their preference.\nUser's message: '{chat_history[-1]['content']}'\nReturn ONLY a JSON object: {{\"{current_q_key}\": \"extracted summary of their preference\"}}"
                res = client.chat.completions.create(
                    model="gpt-5.4-mini",
                    response_format={"type": "json_object"},
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                extracted = json.loads(res.choices[0].message.content or "{}")
                if current_q_key in extracted:
                    style_answers[current_q_key] = extracted[current_q_key]
            except Exception:
                pass # Fail silently and just move on or retry

    # Find the next unanswered question
    next_q = None
    for item in QUESTIONS:
        if item["key"] not in style_answers:
            next_q = item["q"]
            break
            
    if next_q:
        chat_history.append({"role": "assistant", "content": next_q})
        return {
            "style_answers": style_answers,
            "chat_history": chat_history,
            "next_node": "style_questionnaire",
            "current_question": next_q,
            "is_complete": False
        }
    else:
        # All questions answered, transition to dynamic visuals
        return {
            "style_answers": style_answers,
            "next_node": "dynamic_visuals",
            "is_complete": False
        }

def node_dynamic_visuals(state: Dict[str, Any]) -> Dict[str, Any]:
    """Phase 3: Retrieve matching images based on style answers from the Kaggle dataset"""
    chat_history = state.get("chat_history", [])
    style_answers = state.get("style_answers", {})
    room_type = state.get("room_type", "living_room").lower().replace(" ", "_")
    
    # Fallback default
    mapped_style = "modern"
    
    client = get_openai_client()
    if client and style_answers:
        try:
            prompt = (
                f"The user provided these style preferences: {json.dumps(style_answers)}\n"
                f"Which of the following 5 design styles is the closest match?\n"
                f"[boho, industrial, minimalist, modern, scandinavian]\n"
                f"Return ONLY a JSON object: {{\"style\": \"<style>\"}}"
            )
            res = client.chat.completions.create(
                model="gpt-5.4-mini",
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            extracted = json.loads(res.choices[0].message.content or "{}")
            if extracted.get("style") in ["boho", "industrial", "minimalist", "modern", "scandinavian"]:
                mapped_style = extracted["style"]
        except Exception:
            pass

    # Read the dataset metadata
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    metadata_path = os.path.join(root_dir, "static", "metadata.csv")
    
    visual_options = []
    
    if os.path.exists(metadata_path):
        try:
            df = pd.read_csv(metadata_path)
            # Normalize dataset columns just in case
            df.columns = df.columns.str.strip().str.lower()
            
            # Filter by room type and mapped style
            matched = df[(df['room_type'] == room_type) & (df['style'] == mapped_style)]
            
            # If no perfect match for room type, fallback to just style matching
            if matched.empty:
                matched = df[df['style'] == mapped_style]
                
            if not matched.empty:
                # Pick up to 3 random images
                sample_size = min(3, len(matched))
                sampled = matched.sample(n=sample_size)
                
                for i, (_, row) in enumerate(sampled.iterrows()):
                    # The image_path in CSV likely points to "living_room/industrial/img.jpg"
                    # Our static mount is at /static, so the URL should be /static/<image_path>
                    img_path = row['image_path'].replace('\\', '/')
                    visual_options.append({
                        "id": f"option_{i+1}",
                        "label": f"Concept {i+1}",
                        "url": f"/static/{img_path}"
                    })
        except Exception as e:
            print(f"Dataset reading error: {e}")
            
    # Fallback if dataset reading failed or didn't find anything
    if not visual_options:
        visual_options = [
            {"id": "generated_option_1", "label": "Concept 1", "url": "/static/styles/organic_modern.png"},
            {"id": "generated_option_2", "label": "Concept 2", "url": "/static/styles/scandinavian_minimalist.png"},
            {"id": "generated_option_3", "label": "Concept 3", "url": "/static/styles/industrial_chic.png"}
        ]
    
    response_msg = f"Based on your preferences, I determined your overarching style leans towards **{mapped_style.title()}**. I have pulled 3 matching design concepts from our catalog for your {room_type.replace('_', ' ')}. Please select the one that resonates most with your vision:"
    
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
    selected_image_url = state.get("selected_image_url", "")
    
    # Explicitly catch and store the dynamic visual test selection
    if "I select the " in user_input and " style." in user_input:
        match = re.search(r"I select the (.*) style\.", user_input)
        if match:
            preferred_visual_style = match.group(1)
            # Find the URL from the previous visual options to store it
            if len(chat_history) >= 2 and "visual_options" in chat_history[-2]:
                for opt in chat_history[-2]["visual_options"]:
                    if opt["label"] == preferred_visual_style:
                        selected_image_url = opt["url"]
    
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
            model="gpt-5.4-mini",
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
                "selected_image_url": selected_image_url,
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
                "selected_image_url": selected_image_url,
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
            "selected_image_url": selected_image_url,
            "chat_history": chat_history,
            "next_node": "refinement",
            "current_question": "Please try again once the issue is resolved."
        }

def node_synthesis(state: Dict[str, Any]) -> Dict[str, Any]:
    """Phase 4: Synthesis, generative sourcing list, readiness scoring"""
    # 1. Compute Readiness Score (0-100)
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
    
    # Design Sourcing available (40 points)
    b_score = 40 
    
    readiness_score = t_score + dm_score + scope_score + b_score
    
    # 2. LLM Generates Material & Furniture Sourcing List
    client = get_openai_client()
    sourcing_list = []
    design_dna = state.get("design_dna", "Custom Classic")
    
    if client:
        try:
            prompt = f"Based on the design DNA '{design_dna}', recommend exactly 5 highly specific material, texture, or statement furniture items that a designer should source. Example output array: ['Benjamin Moore Swiss Coffee Paint', 'Unlacquered Brass Faucets', 'Curved Bouclé Accent Chair']. Return JSON format: {{\"sourcing_list\": [\"item 1\", \"item 2\", \"item 3\", \"item 4\", \"item 5\"]}}"
            res = client.chat.completions.create(
                model="gpt-5.4-mini",
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            extracted = json.loads(res.choices[0].message.content or "{}")
            sourcing_list = extracted.get("sourcing_list", [])
        except Exception:
            sourcing_list = ["Error generating sourcing list"]
            
    summary_msg = (
        f"Thank you for completing the Taste Discovery process. "
        f"I have compiled your Project Design Brief.\n\n"
        f"📊 **Design DNA:** {design_dna}\n"
        f"📏 **Estimated Space Area:** {state.get('area_sqft', 300)} sq ft\n"
        f"📋 **Project Readiness Score:** {readiness_score}/100\n\n"
        f"I am compiling this information into a Project Intelligence Report for your Architect/Designer, which now includes a customized Material Sourcing Board. "
        f"They will reach out to schedule your 1-on-1 design consultation."
    )
    
    chat_history = state.get("chat_history", [])
    chat_history.append({"role": "assistant", "content": summary_msg})
    
    return {
        "readiness_score": readiness_score,
        "sourcing_list": sourcing_list,
        "chat_history": chat_history,
        "is_complete": True,
        "next_node": "END"
    }
