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
        """GET /{page-id}/insights for page_post_engagements."""
        if not self.fb_access_token or not self.fb_page_id:
            logger.warning("AnalyticsService: Missing Facebook credentials.")
            return {"error": "Missing Facebook credentials"}

        url = f"https://graph.facebook.com/{self.api_version}/{self.fb_page_id}/insights"
        params = {
            "metric": "page_post_engagements",
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
        """GET /{ig-id}/insights for reach, accounts_engaged."""
        if not self.ig_access_token:
            logger.warning("AnalyticsService: Missing Instagram access token.")
            return {"error": "Missing Instagram access token"}

        ig_id = self._get_ig_business_id()
        if not ig_id:
            return {"error": "Could not resolve Instagram business account ID"}

        url = f"https://graph.facebook.com/{self.api_version}/{ig_id}/insights"
        params = {
            "metric": "reach,accounts_engaged",
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
                if "total_value" in metric:
                    total = metric["total_value"].get("value", 0)
                else:
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

    # ---- Fetch specific Post Insights ----

    def _fetch_ig_post_insights(self, media_id: str) -> dict:
        if not self.ig_access_token:
            return {"error": "Missing Instagram access token"}
        
        try:
            # 1. Fetch likes and comments
            url_media = f"https://graph.facebook.com/{self.api_version}/{media_id}"
            params_media = {"fields": "like_count,comments_count", "access_token": self.ig_access_token}
            resp_m = requests.get(url_media, params=params_media, timeout=10)
            resp_m.raise_for_status()
            data_m = resp_m.json()
            
            likes = data_m.get("like_count", 0)
            comments = data_m.get("comments_count", 0)

            # 2. Fetch reach & engagement
            url_ins = f"https://graph.facebook.com/{self.api_version}/{media_id}/insights"
            params_ins = {"metric": "reach,saved", "access_token": self.ig_access_token}
            resp_ins = requests.get(url_ins, params=params_ins, timeout=10)
            reach, impressions = 0, 0
            if resp_ins.status_code == 200:
                data_ins = resp_ins.json().get("data", [])
                for metric in data_ins:
                    name = metric.get("name")
                    values = metric.get("values", [])
                    val = values[0].get("value", 0) if values else 0
                    if name == "reach":
                        reach = val
                    elif name == "impressions": # Should not happen now, but safe
                        impressions = val

            return {"likes": likes, "comments": comments, "reach": reach, "impressions": impressions}
        except Exception as e:
            logger.error(f"AnalyticsService: IG post {media_id} insights error: {e}")
            return {"error": str(e)}

    def _fetch_fb_post_insights(self, post_id: str) -> dict:
        if not self.fb_access_token:
            return {"error": "Missing FB token"}
        try:
            # 1. Fetch likes and comments
            url = f"https://graph.facebook.com/{self.api_version}/{post_id}"
            params = {
                "fields": "likes.summary(true),comments.summary(true)",
                "access_token": self.fb_access_token
            }
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            likes = data.get("likes", {}).get("summary", {}).get("total_count", 0)
            comments = data.get("comments", {}).get("summary", {}).get("total_count", 0)
            
            # 2. Try fetching reach and impressions
            reach, impressions = 0, 0
            params_ins = {
                "fields": "insights.metric(post_impressions,post_impressions_unique)",
                "access_token": self.fb_access_token
            }
            resp_ins = requests.get(url, params=params_ins, timeout=10)
            if resp_ins.status_code == 200:
                insights_data = resp_ins.json().get("insights", {}).get("data", [])
                for metric in insights_data:
                    name = metric.get("name")
                    values = metric.get("values", [])
                    val = values[0].get("value", 0) if values else 0
                    if name == "post_impressions_unique":
                        reach = val
                    elif name == "post_impressions":
                        impressions = val
                    
            return {"likes": likes, "comments": comments, "reach": reach, "impressions": impressions}
        except Exception as e:
            logger.error(f"AnalyticsService: FB post {post_id} error: {e}")
            return {"error": str(e)}

    async def update_all_post_analytics(self, session: AsyncSession):
        """Fetch fresh post-level insights for all published posts and save them."""
        stmt = select(Post).where(Post.status == PostStatus.published, Post.platform_post_id.is_not(None))
        result = await session.execute(stmt)
        posts = result.scalars().all()

        for post in posts:
            if post.platform.value == "instagram":
                metrics = self._fetch_ig_post_insights(post.platform_post_id)
            elif post.platform.value == "facebook":
                metrics = self._fetch_fb_post_insights(post.platform_post_id)
            else:
                continue
            
            if "error" not in metrics:
                a_stmt = select(Analytics).where(Analytics.post_id == post.id)
                a_result = await session.execute(a_stmt)
                analytics = a_result.scalar_one_or_none()
                
                if not analytics:
                    analytics = Analytics(post_id=post.id)
                    session.add(analytics)
                
                analytics.likes = metrics.get("likes", analytics.likes)
                analytics.comments = metrics.get("comments", analytics.comments)
                analytics.reach = metrics.get("reach", analytics.reach)
                analytics.impressions = metrics.get("impressions", analytics.impressions)
                
                # Combine likes and comments into engagement, plus any other actions theoretically
                analytics.engagement = analytics.likes + analytics.comments
                eng_rate = (analytics.engagement / analytics.reach * 100) if analytics.reach and analytics.reach > 0 else 0.0
                analytics.engagement_rate = round(eng_rate, 2)
                analytics.fetched_at = datetime.now(timezone.utc)
        
        await session.commit()
        logger.info("AnalyticsService: Finished updating all post-level analytics.")

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

    async def delete_platform_post(self, platform: str, platform_post_id: str) -> bool:
        """Deletes a post directly from Facebook or Instagram Graph API"""
        if not platform_post_id:
            return False
            
        try:
            url = f"https://graph.facebook.com/{self.api_version}/{platform_post_id}"
            
            if platform.lower() == "instagram":
                token = self.ig_access_token
            elif platform.lower() == "facebook":
                token = self.fb_access_token
            else:
                return False
                
            if not token:
                logger.warning(f"AnalyticsService: Missing token for {platform}")
                return False
                
            params = {"access_token": token}
            resp = requests.delete(url, params=params, timeout=10)
            resp.raise_for_status()
            logger.info(f"AnalyticsService: Successfully deleted {platform} post {platform_post_id} from Graph API.")
            return True
        except Exception as e:
            logger.error(f"AnalyticsService: Failed to delete {platform} post {platform_post_id}. Ensure token has Delete permissions: {e}")
            # If it's a 400 error because the post was already deleted on IG directly, return True to clear our DB.
            return False
