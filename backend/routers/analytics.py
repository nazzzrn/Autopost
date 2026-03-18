"""
Analytics router — serves KPI overview, time-series, per-post analytics,
and a manual refresh trigger.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from database import get_db
from db_models import Post, Analytics
from analytics_service import AnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])

analytics_service = AnalyticsService()


@router.get("/overview")
async def get_overview(db: AsyncSession = Depends(get_db)):
    """KPI summary: total reach, impressions, avg engagement rate."""
    overview = await analytics_service.get_overview(db)
    return overview


@router.get("/insights")
async def get_insights(db: AsyncSession = Depends(get_db)):
    """Time-series analytics data for charting."""
    data = await analytics_service.get_insights_timeseries(db)
    return data


@router.get("/posts")
async def get_post_analytics(db: AsyncSession = Depends(get_db)):
    """Per-post analytics with post metadata."""
    data = await analytics_service.get_post_analytics(db)
    return data


@router.post("/refresh")
async def refresh_analytics(db: AsyncSession = Depends(get_db)):
    """Fetch fresh data from Facebook & Instagram APIs."""
    fb_data = analytics_service.fetch_facebook_page_insights()
    ig_data = analytics_service.fetch_instagram_insights()

    # Wait for post-level analytics to update
    await analytics_service.update_all_post_analytics(db)

    return {
        "facebook": fb_data,
        "instagram": ig_data,
        "message": "Fresh data fetched from platform APIs. Post-level analytics updated successfully."
    }

@router.delete("/posts/{post_id}")
async def delete_post(post_id: str, db: AsyncSession = Depends(get_db)):
    """Deletes a post from the database and Graph API."""
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalars().first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    # Attempt to delete from external platform first
    if post.platform_post_id:
        success = await analytics_service.delete_platform_post(post.platform, post.platform_post_id)
        if not success:
            logger.warning(f"Failed to delete {post.platform_post_id} from {post.platform}, but proceeding with local delete.")
            
    # Delete locally (delete analytics to be safe then post)
    await db.execute(delete(Analytics).where(Analytics.post_id == post_id))
    await db.delete(post)
    await db.commit()
    return {"message": "Post deleted successfully"}
