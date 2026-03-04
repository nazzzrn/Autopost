from contextlib import asynccontextmanager
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
from database import init_db
from scheduler_service import start_scheduler, stop_scheduler
from routers import posts as posts_router, analytics as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info("Starting up — initializing DB and scheduler...")
    await init_db()
    start_scheduler()
    yield
    logger.info("Shutting down — stopping scheduler...")
    stop_scheduler()


app = FastAPI(title="Content Workflow Automation Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount new routers
app.include_router(posts_router.router)
app.include_router(analytics_router.router)

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

@app.post("/workflow/reset")
async def reset_workflow():
    global current_state
    current_state = {
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
        "error": None,
    }
    logger.info("Workflow state reset to initial.")
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
        # Move to Image Review WITHOUT auto-generating an image.
        # User can generate via button or upload manually.
        current_state["captions"] = request.captions  # Update with any edits
        current_state["current_step"] = "review_image"
    else:
        # Regenerate
        if current_state["regenerate_count_caption"] >= 3:
            raise HTTPException(status_code=400, detail="Max regeneration limit reached")
        
        current_state["feedback"] = request.feedback or ""
        from agent_workflow import generate_caption_node
        res_cap = generate_caption_node(current_state)
        current_state.update(res_cap)
        current_state["current_step"] = "review_caption"  # Stay here
        
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
    from datetime import datetime
    from database import async_session
    from db_models import Post, PostStatus, PlatformEnum

    current_state["schedule_time"] = request.schedule_time.isoformat()
    # Use naive local time — browser sends local time without tz info,
    # and the server clock is also local, so they match.
    schedule_dt = request.schedule_time.replace(tzinfo=None)
    now = datetime.now()

    if schedule_dt > now:
        # Future time — save to DB as 'scheduled', the scheduler will publish later
        async with async_session() as session:
            for platform in current_state.get("platforms", []):
                p_enum = PlatformEnum.instagram if platform.lower() == "instagram" else PlatformEnum.facebook
                post = Post(
                    platform=p_enum,
                    caption=current_state.get("captions", {}).get(platform, ""),
                    image_url=current_state.get("image_path"),
                    status=PostStatus.scheduled,
                    scheduled_time=schedule_dt,
                )
                session.add(post)
            await session.commit()

        current_state["publish_status"] = {p: "Scheduled" for p in current_state.get("platforms", [])}
        current_state["current_step"] = "completed"
        logger.info(f"Posts scheduled for {schedule_dt.isoformat()} (local time) and saved to DB.")
    else:
        # Past or now — publish immediately
        current_state["current_step"] = "publish"

    return current_state


@app.post("/workflow/publish")
async def publish():
    global current_state
    from datetime import datetime, timezone
    from database import async_session
    from db_models import Post, PostStatus, PlatformEnum

    from agent_workflow import publish_node
    res_pub = publish_node(current_state)
    current_state.update(res_pub)
    current_state["current_step"] = "completed"

    # Save published posts to DB so they show in the calendar
    async with async_session() as session:
        for platform, status_msg in current_state.get("publish_status", {}).items():
            p_lower = platform.lower()
            if p_lower in ("instagram", "facebook"):
                p_enum = PlatformEnum(p_lower)
                post = Post(
                    platform=p_enum,
                    caption=current_state.get("captions", {}).get(platform, ""),
                    image_url=current_state.get("image_path"),
                    status=PostStatus.published if "Published" in status_msg else PostStatus.failed,
                    published_time=datetime.now(timezone.utc) if "Published" in status_msg else None,
                    scheduled_time=datetime.fromisoformat(current_state["schedule_time"]) if current_state.get("schedule_time") else datetime.now(timezone.utc),
                )
                session.add(post)
        await session.commit()
    logger.info("Published posts saved to DB.")

    return current_state

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
