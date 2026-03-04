"""
Analytics service — fetches insights from Facebook and Instagram Graph APIs.
Stores metrics in the analytics table.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional

import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db_models import Analytics, Post, PostStatus

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Fetches page-level and post-level insights from FB/IG APIs."""

    def __init__(self):
        self.fb_access_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
        self.fb_page_id = os.getenv("FACEBOOK_PAGE_ID", "")
        self.ig_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
        self.ig_page_id = os.getenv("INSTAGRAM_PAGE_ID", "")
        self.api_version = "v21.0"

    # ---- Facebook Page Insights ----

    def fetch_facebook_page_insights(self) -> dict:
        """GET /{page-id}/insights for page_impressions, page_reach, page_engaged_users."""
        if not self.fb_access_token or not self.fb_page_id:
            logger.warning("AnalyticsService: Missing Facebook credentials.")
            return {"error": "Missing Facebook credentials"}

        url = f"https://graph.facebook.com/{self.api_version}/{self.fb_page_id}/insights"
        params = {
            "metric": "page_impressions,page_post_engagements,page_fan_adds",
            "period": "day",
            "access_token": self.fb_access_token,
        }

        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json().get("data", [])

            result = {}
            for metric in data:
                name = metric.get("name", "")
                values = metric.get("values", [])
                total = sum(v.get("value", 0) for v in values if isinstance(v.get("value"), (int, float)))
                result[name] = total

            logger.info(f"AnalyticsService: Facebook page insights fetched: {result}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"AnalyticsService: Facebook insights error: {e}")
            return {"error": str(e)}

    # ---- Instagram Insights ----

    def _get_ig_business_id(self) -> Optional[str]:
        """
        Resolve Instagram Business Account ID.
        If INSTAGRAM_PAGE_ID is already set (17841... format), use it directly.
        Otherwise, try to discover it from the linked Facebook Page.
        """
        # INSTAGRAM_PAGE_ID is typically the IG Business Account ID itself
        if self.ig_page_id:
            return self.ig_page_id

        # Fallback: try to discover from Facebook Page
        if self.fb_page_id and self.fb_access_token:
            url = f"https://graph.facebook.com/{self.api_version}/{self.fb_page_id}"
            params = {
                "fields": "instagram_business_account",
                "access_token": self.fb_access_token,
            }
            try:
                resp = requests.get(url, params=params, timeout=10)
                resp.raise_for_status()
                ig_acct = resp.json().get("instagram_business_account", {})
                return ig_acct.get("id")
            except Exception as e:
                logger.error(f"AnalyticsService: Could not resolve IG business ID: {e}")

        return None

    def fetch_instagram_insights(self) -> dict:
        """GET /{ig-id}/insights for impressions, reach, accounts_engaged."""
        if not self.ig_access_token:
            logger.warning("AnalyticsService: Missing Instagram access token.")
            return {"error": "Missing Instagram access token"}

        ig_id = self._get_ig_business_id()
        if not ig_id:
            return {"error": "Could not resolve Instagram business account ID"}

        url = f"https://graph.facebook.com/{self.api_version}/{ig_id}/insights"
        params = {
            "metric": "impressions,reach",
            "period": "day",
            "metric_type": "total_value",
            "access_token": self.ig_access_token,
        }

        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json().get("data", [])

            result = {}
            for metric in data:
                name = metric.get("name", "")
                values = metric.get("values", [])
                total = sum(v.get("value", 0) for v in values if isinstance(v.get("value"), (int, float)))
                result[name] = total

            logger.info(f"AnalyticsService: Instagram insights fetched: {result}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"AnalyticsService: Instagram insights error: {e}")
            return {"error": str(e)}

    # ---- Store analytics for a post ----

    async def store_post_analytics(
        self, session: AsyncSession, post_id: str, reach: int, impressions: int, engagement: int
    ):
        """Persist analytics row for a specific post."""
        eng_rate = (engagement / reach * 100) if reach > 0 else 0.0

        analytics = Analytics(
            post_id=post_id,
            reach=reach,
            impressions=impressions,
            engagement=engagement,
            engagement_rate=round(eng_rate, 2),
            fetched_at=datetime.now(timezone.utc),
        )
        session.add(analytics)
        await session.commit()
        logger.info(f"AnalyticsService: Stored analytics for post {post_id}")
        return analytics

    # ---- Aggregate helpers ----

    async def get_overview(self, session: AsyncSession) -> dict:
        """Return KPI summary: total reach, impressions, avg engagement rate."""
        stmt = select(Analytics)
        result = await session.execute(stmt)
        rows = result.scalars().all()

        if not rows:
            return {
                "total_reach": 0,
                "total_impressions": 0,
                "avg_engagement_rate": 0.0,
                "total_posts_tracked": 0,
            }

        total_reach = sum(r.reach for r in rows)
        total_impressions = sum(r.impressions for r in rows)
        avg_eng = sum(r.engagement_rate for r in rows) / len(rows) if rows else 0.0

        return {
            "total_reach": total_reach,
            "total_impressions": total_impressions,
            "avg_engagement_rate": round(avg_eng, 2),
            "total_posts_tracked": len(rows),
        }

    async def get_post_analytics(self, session: AsyncSession) -> list[dict]:
        """Return per-post analytics joined with post info."""
        stmt = select(Analytics).order_by(Analytics.fetched_at.desc())
        result = await session.execute(stmt)
        rows = result.scalars().all()

        enriched = []
        for row in rows:
            # Eagerly load the post
            post_stmt = select(Post).where(Post.id == row.post_id)
            post_result = await session.execute(post_stmt)
            post = post_result.scalar_one_or_none()

            entry = row.to_dict()
            if post:
                entry["post"] = post.to_dict()
            enriched.append(entry)

        return enriched

    async def get_insights_timeseries(self, session: AsyncSession) -> list[dict]:
        """Return analytics rows ordered by time for charting."""
        stmt = select(Analytics).order_by(Analytics.fetched_at.asc())
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return [r.to_dict() for r in rows]
