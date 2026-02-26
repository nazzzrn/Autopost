from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import uvicorn
import os

load_dotenv()

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

from models import StartWorkflowRequest, ReviewCaptionRequest, ReviewImageRequest, ScheduleRequest, WorkflowState
from agent_workflow import app as workflow_app, AgentState

app = FastAPI(title="Content Workflow Automation Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for state (Single user = single state for simplicity)
# In a real multi-user app, use a database or session-dict.
current_state: AgentState = {
    "topic": "",
    "platforms": [],
    "captions": {},
    "image_path": None,
    "schedule_time": None,
    "publish_status": {},
    "feedback": "",
    "regenerate_count_caption": 0,
    "regenerate_count_image": 0,
    "current_step": "prompt",
    "caption_options": {},
    "error": None
}

@app.post("/workflow/start")
async def start_workflow(request: StartWorkflowRequest):
    global current_state
    # Reset state
    current_state = {
        "topic": request.prompt,
        "platforms": [],
        "captions": {},
        "image_path": None,
        "schedule_time": None,
        "publish_status": {},
        "feedback": "",
        "regenerate_count_caption": 0,
        "regenerate_count_image": 0,
        "current_step": "prompt",
        "caption_options": {},
        "error": None
    }
    
    # Run the graph. It stops at review_caption because there's no outgoing edge.
    result = workflow_app.invoke(current_state)
    current_state.update(result)
    current_state["current_step"] = "review_caption"
    
    return current_state

@app.get("/workflow/state")
async def get_state():
    return current_state

class GenerateCaptionRequest(BaseModel):
    platform: str
    topic: str
    feedback: Optional[str] = None

@app.post("/workflow/generate-caption")
async def generate_caption_endpoint(req: GenerateCaptionRequest):
    logger.info(f"API: Generating caption for {req.platform}")
    
    # We call the service directly
    from agent_workflow import gemini
    
    options = gemini.generate_caption(req.topic, req.platform, req.feedback)
    
    # Update global state
    current_state["caption_options"][req.platform] = options
    if options:
        current_state["captions"][req.platform] = options[0] # Default select first
        
    return current_state

@app.post("/workflow/review-caption")
async def review_caption(request: ReviewCaptionRequest):
    global current_state
    
    if request.accepted:
        # Move to Image Generation
        from agent_workflow import generate_image_node
        current_state["captions"] = request.captions # Update with any edits
        
        res_img = generate_image_node(current_state)
        current_state.update(res_img)
        current_state["current_step"] = "review_image"
    else:
        # Regenerate
        if current_state["regenerate_count_caption"] >= 3:
            raise HTTPException(status_code=400, detail="Max regeneration limit reached")
        
        current_state["feedback"] = request.feedback or ""
        from agent_workflow import generate_caption_node
        res_cap = generate_caption_node(current_state)
        current_state.update(res_cap)
        current_state["current_step"] = "review_caption" # Stay here
        
    return current_state

@app.post("/workflow/generate-image")
async def generate_image_endpoint(req: StartWorkflowRequest): # Use same schema for topic
    global current_state
    logger.info(f"API: Generating image for topic: {req.prompt}")
    
    from agent_workflow import gemini
    image_url = gemini.generate_image(req.prompt, current_state.get("feedback", ""))
    
    current_state["image_path"] = image_url
    return current_state

@app.post("/workflow/review-image")
async def review_image(request: ReviewImageRequest):
    global current_state
    
    if request.image_path:
        # User uploaded/provided a path
        current_state["image_path"] = request.image_path
    
    if request.accepted:
        # Move to Schedule
        current_state["current_step"] = "schedule"
    else:
        if current_state["regenerate_count_image"] >= 3:
            raise HTTPException(status_code=400, detail="Max regeneration limit reached")
            
        current_state["feedback"] = request.feedback or ""
        from agent_workflow import generate_image_node
        res_img = generate_image_node(current_state)
        current_state.update(res_img)
        current_state["current_step"] = "review_image"
        
    return current_state

@app.post("/workflow/schedule")
async def schedule(request: ScheduleRequest):
    global current_state
    current_state["schedule_time"] = request.schedule_time.isoformat()
    # Move to Publish
    # Actually wait for explicit "Publish" action or do it now?
    # Logic: UI has "Publish" button on Schedule page?
    # Let's assume this saves the time and moves to "ready to publish" state or publishes.
    # The prompt says "Sequential Publishing Stage" follows Schedule.
    
    # Let's update state to 'publishing' and trigger publish immediately 
    # or return state so frontend calls /publish
    
    current_state["current_step"] = "publish"
    return current_state

@app.post("/workflow/publish")
async def publish():
    global current_state
    
    from agent_workflow import publish_node
    res_pub = publish_node(current_state)
    current_state.update(res_pub)
    current_state["current_step"] = "completed"
    
    return current_state

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
