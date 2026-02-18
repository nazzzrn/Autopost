from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Optional
import operator
from datetime import datetime
from services import GeminiService, InstagramService, FacebookService, LinkedInService, mock_generate_image
import os
import logging

logger = logging.getLogger(__name__)

# Define the state as a TypedDict for LangGraph
class AgentState(TypedDict):
    topic: str
    platforms: List[str]
    captions: dict
    caption_options: dict
    image_path: Optional[str]
    schedule_time: Optional[str] # Store as string for JSON serialization ease in graph
    publish_status: dict
    feedback: str
    regenerate_count_caption: int
    regenerate_count_image: int
    current_step: str
    error: Optional[str]

# Initialize Services
gemini = GeminiService()
instagram = InstagramService()
facebook = FacebookService()
linkedin = LinkedInService()

# Nodes

def parse_prompt_node(state: AgentState):
    # In a real app, use Gemini to extract. For now, simple logic or simulated extraction.
    # If topic is empty, we assume it's the start and we need to parse.
    # But since the prompt comes from the user to the API, we might just set it in the initial state.
    # Let's assume the prompt was passed in the initial state "topic" (wrapper).
    
    prompt = state.get("topic", "")
    logger.info(f"parse_prompt_node: Received prompt: {prompt}")
    
    # Use Gemini to parse
    # Simple prompt to extract JSON
    extraction_prompt = f"""
    Extract the following from the user prompt:
    1. Topic (summary of what to post about)
    2. Platforms (list of Instagram, Facebook, LinkedIn)
    3. Schedule Time (if mentioned, else null)
    
    User Prompt: {prompt}
    
    Return pure JSON format: {{ "topic": "...", "platforms": ["..."], "schedule_time": "..." }}
    """
    
    try:
        response = gemini.model.generate_content(extraction_prompt)
        import json
        import re
        # Clean markdown code blocks if any
        text = response.text
        text = re.sub(r"```json", "", text)
        text = re.sub(r"```", "", text)
        data = json.loads(text)
        
        return {
            "topic": data.get("topic", prompt),
            "platforms": [p.title() for p in data.get("platforms", ["Instagram", "Facebook", "LinkedIn"])],
            "schedule_time": data.get("schedule_time"),
            "current_step": "review_caption", # Next step logic handled by edges usually, but we update status
            "feedback": ""
        }
    except Exception as e:
        print(f"Error parsing prompt: {e}")
        return {
            "topic": prompt, 
            "platforms": ["Instagram", "Facebook", "LinkedIn"],
            "current_step": "review_caption"
        }

def generate_caption_node(state: AgentState):
    captions = state.get("captions", {})
    caption_options = state.get("caption_options", {})
    platforms = state.get("platforms", [])
    topic = state.get("topic", "")
    feedback = state.get("feedback", "")
    
    for platform in platforms:
        # Only regenerate if not already present or if feedback exists (implies regeneration)
        logger.info(f"generate_caption_node: Generating for {platform} with feedback: {feedback}")
        options = gemini.generate_caption(topic, platform, feedback)
        
        caption_options[platform] = options
        
        # Default to the first option if no caption is currently selected (or if we are regenerating)
        # If regenerating with feedback, we likely want to overwrite the current selection with the new best option (first one)
        if options:
            captions[platform] = options[0]
            
        logger.debug(f"Generated {len(options)} options for {platform}")
        
    return {
        "captions": captions,
        "caption_options": caption_options,
        "current_step": "review_caption",
        "feedback": "", # Clear feedback after usage
        "regenerate_count_caption": state.get("regenerate_count_caption", 0) + 1
    }

def review_caption_node(state: AgentState):
    # This node is a placeholder for the human interrupt.
    # It doesn't do much processing, just holds state.
    return {"current_step": "review_caption"}

def generate_image_node(state: AgentState):
    topic = state.get("topic", "")
    feedback = state.get("feedback", "")
    
    # Simulate image generation
    description = gemini.generate_image_description(topic, feedback)
    image_url = mock_generate_image(description)
    
    return {
        "image_path": image_url,
        "current_step": "review_image",
        "feedback": "",
        "regenerate_count_image": state.get("regenerate_count_image", 0) + 1
    }

def review_image_node(state: AgentState):
    # Placeholder for human interrupt
    return {"current_step": "review_image"}

def schedule_node(state: AgentState):
    # Placeholder for human interrupt to pick time
    # If time was parsed, it might skip, but user wants to confirm.
    return {"current_step": "schedule"}

def publish_node(state: AgentState):
    platforms = state.get("platforms", [])
    captions = state.get("captions", {})
    image = state.get("image_path", "")
    time = state.get("schedule_time", "")
    status = {}
    
    # Sequential publishing order: Instagram -> Facebook -> LinkedIn
    # Filter platforms to this order
    order = ["Instagram", "Facebook", "LinkedIn"]
    
    for p in order:
        if p in platforms:
            # Check for specific service
            if p == "Instagram":
                res = instagram.publish_post(image, captions.get(p, ""), time)
            elif p == "Facebook":
                res = facebook.publish_post(image, captions.get(p, ""), time)
            elif p == "LinkedIn":
                res = linkedin.publish_post(image, captions.get(p, ""), time)
            else:
                res = "Unknown platform"
            status[p] = res
            logger.info(f"publish_node: {p} status: {res}")
            
    return {
        "publish_status": status,
        "current_step": "completed"
    }

# Edges

def route_caption(state: AgentState):
    # If regeneration count > 3, force move to image or error?
    # Requirement: "Max regeneration limit = 3"
    # If 3 reached, maybe we stop allowing regenerate?
    # Logic is handled by the API caller (Review Action).
    # If user accepts, go to generate_image.
    # If user rejects, go to generate_caption.
    pass 

# Creating the Graph
workflow = StateGraph(AgentState)

workflow.add_node("parse_prompt", parse_prompt_node)
workflow.add_node("generate_caption", generate_caption_node)
workflow.add_node("review_caption", review_caption_node)
workflow.add_node("generate_image", generate_image_node)
workflow.add_node("review_image", review_image_node)
workflow.add_node("schedule", schedule_node)
workflow.add_node("publish", publish_node)

# Defining flow
# Start -> Parse -> Generate Caption -> Review Caption
# Start -> Parse -> Review Caption (User triggers generation manually)
workflow.set_entry_point("parse_prompt")
workflow.add_edge("parse_prompt", "review_caption")
# workflow.add_edge("generate_caption", "review_caption") # Skipped for manual trigger

# Review Caption interactions are handled by interrupting the graph or conditional edges based on state input?
# With LangGraph, we can use an 'interrupt_before' logic or just have the API update the state and resume.
# For this simple API-driven approach without persistent background worker, 
# The API will trigger the next node based on user action.
# However, to visualize 'flow', we define edges.

# We will handle the "Human in loop" by returning to the client and waiting for the next API call to trigger the next step.
# The graph execution will be "step-by-step".

workflow.add_edge("review_caption", "generate_image") # Logical next step if accepted
workflow.add_edge("generate_image", "review_image")
workflow.add_edge("review_image", "schedule")
workflow.add_edge("schedule", "publish")
workflow.add_edge("publish", END)

# Compile
app = workflow.compile()
