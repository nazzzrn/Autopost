"""
Analytics router — serves KPI overview, time-series, per-post analytics,
and a manual refresh trigger.
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
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
async def refresh_analytics():
    """Fetch fresh data from Facebook & Instagram APIs."""
    fb_data = analytics_service.fetch_facebook_page_insights()
    ig_data = analytics_service.fetch_instagram_insights()

    return {
        "facebook": fb_data,
        "instagram": ig_data,
        "message": "Fresh data fetched from platform APIs. Post-level analytics are stored when posts are published."
    }
