"""
Posts CRUD router.
Manages draft / scheduled / published posts in the database.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from db_models import Post, PostStatus, PlatformEnum

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/posts", tags=["posts"])


# ---- Request / Response Schemas ----

class CreatePostRequest(BaseModel):
    platform: str  # "instagram" or "facebook"
    caption: str = ""
    image_url: Optional[str] = None
    status: str = "draft"  # "draft" or "scheduled"
    scheduled_time: Optional[str] = None  # ISO format


class UpdatePostRequest(BaseModel):
    caption: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = None
    scheduled_time: Optional[str] = None


# ---- Endpoints ----

@router.post("")
async def create_post(req: CreatePostRequest, db: AsyncSession = Depends(get_db)):
    """Create a new draft or scheduled post."""
    try:
        platform = PlatformEnum(req.platform.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid platform: {req.platform}. Use 'instagram' or 'facebook'.")

    try:
        status = PostStatus(req.status.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {req.status}. Use 'draft' or 'scheduled'.")

    sched_time = None
    if req.scheduled_time:
        try:
            sched_time = datetime.fromisoformat(req.scheduled_time)
            if sched_time.tzinfo is None:
                sched_time = sched_time.replace(tzinfo=timezone.utc)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid scheduled_time format. Use ISO 8601.")

    post = Post(
        platform=platform,
        caption=req.caption,
        image_url=req.image_url,
        status=status,
        scheduled_time=sched_time,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)

    logger.info(f"Posts: Created post {post.id} ({platform.value}, {status.value})")
    return post.to_dict()


@router.get("")
async def list_posts(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """Return all posts. Optionally filter by status."""
    stmt = select(Post).order_by(Post.created_at.desc())

    if status:
        try:
            status_enum = PostStatus(status.lower())
            stmt = stmt.where(Post.status == status_enum)
        except ValueError:
            pass  # Ignore invalid filter

    result = await db.execute(stmt)
    posts = result.scalars().all()
    return [p.to_dict() for p in posts]


@router.get("/{post_id}")
async def get_post(post_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single post by ID."""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post.to_dict()


@router.put("/{post_id}")
async def update_post(post_id: str, req: UpdatePostRequest, db: AsyncSession = Depends(get_db)):
    """Update a post's scheduled_time, status, caption, or image_url."""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if req.caption is not None:
        post.caption = req.caption
    if req.image_url is not None:
        post.image_url = req.image_url
    if req.status is not None:
        try:
            post.status = PostStatus(req.status.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {req.status}")
    if req.scheduled_time is not None:
        try:
            sched = datetime.fromisoformat(req.scheduled_time)
            if sched.tzinfo is None:
                sched = sched.replace(tzinfo=timezone.utc)
            post.scheduled_time = sched
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid scheduled_time format.")

    post.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(post)

    logger.info(f"Posts: Updated post {post_id}")
    return post.to_dict()


@router.delete("/{post_id}")
async def delete_post(post_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a post."""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(post)
    await db.commit()

    logger.info(f"Posts: Deleted post {post_id}")
    return {"detail": "Post deleted", "id": post_id}
