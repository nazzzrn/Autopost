"""
APScheduler-based scheduling engine.
Runs a background job every 60 seconds to publish posts whose scheduled_time has passed.
"""

import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from database import async_session
from db_models import Post, PostStatus

logger = logging.getLogger(__name__)

# Module-level scheduler instance
scheduler = AsyncIOScheduler()


async def _process_scheduled_posts():
    """Fetch due posts and publish them via existing platform services."""
    now = datetime.now()  # Use local server time (matches how schedule_time is stored)
    logger.info(f"Scheduler tick — checking for posts due before {now.isoformat()}")

    async with async_session() as session:
        stmt = select(Post).where(
            Post.status == PostStatus.scheduled,
            Post.scheduled_time <= now,
        )
        result = await session.execute(stmt)
        due_posts = result.scalars().all()

        if not due_posts:
            logger.info("Scheduler: No posts due.")
            return

        # Import platform services lazily to avoid circular imports
        from services import InstagramService, FacebookService

        instagram = InstagramService()
        facebook = FacebookService()

        for post in due_posts:
            platform_name = post.platform.value if post.platform else ""
            logger.info(f"Scheduler: Publishing post {post.id} to {platform_name}")

            try:
                if platform_name == "instagram":
                    result_msg = instagram.publish_post(
                        post.image_url or "", post.caption or "", ""
                    )
                elif platform_name == "facebook":
                    result_msg = facebook.publish_post(
                        post.image_url or "", post.caption or "", ""
                    )
                else:
                    result_msg = f"Unknown platform: {platform_name}"

                if "Published" in result_msg:
                    post.status = PostStatus.published
                    post.published_time = datetime.now()
                    logger.info(f"Scheduler: Post {post.id} published successfully.")
                else:
                    post.status = PostStatus.failed
                    logger.warning(f"Scheduler: Post {post.id} failed — {result_msg}")

            except Exception as e:
                post.status = PostStatus.failed
                logger.error(f"Scheduler: Error publishing post {post.id}: {e}")

        await session.commit()


def start_scheduler():
    """Start the APScheduler background job. Call on FastAPI startup."""
    scheduler.add_job(
        _process_scheduled_posts,
        trigger=IntervalTrigger(seconds=60),
        id="publish_scheduled_posts",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — polling every 60 seconds.")


def stop_scheduler():
    """Gracefully shut down the scheduler. Call on FastAPI shutdown."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
