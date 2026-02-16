from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WorkflowState(BaseModel):
    topic: str = ""
    platforms: List[str] = []
    captions: dict = {}  # platform -> caption
    image_path: Optional[str] = None
    schedule_time: Optional[datetime] = None
    publish_status: dict = {} # platform -> status
    feedback: str = ""
    regenerate_count_caption: int = 0
    regenerate_count_image: int = 0
    current_step: str = "prompt"

class StartWorkflowRequest(BaseModel):
    prompt: str

class ReviewCaptionRequest(BaseModel):
    captions: dict
    accepted: bool
    feedback: Optional[str] = None

class ReviewImageRequest(BaseModel):
    accepted: bool
    feedback: Optional[str] = None
    image_path: Optional[str] = None # For upload

class ScheduleRequest(BaseModel):
    schedule_time: datetime
