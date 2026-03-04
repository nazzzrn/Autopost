"""
SQLAlchemy ORM models for the posts and analytics tables.
"""

import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, Enum, DateTime, Float, ForeignKey, Integer
)
from sqlalchemy.orm import relationship
from database import Base


# ---------- Enums ----------

class PlatformEnum(str, enum.Enum):
    instagram = "instagram"
    facebook = "facebook"


class PostStatus(str, enum.Enum):
    draft = "draft"
    scheduled = "scheduled"
    published = "published"
    failed = "failed"


# ---------- Models ----------

def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, nullable=True)  # nullable for now (single-user)
    platform = Column(Enum(PlatformEnum), nullable=False)
    caption = Column(Text, nullable=False, default="")
    image_url = Column(Text, nullable=True)
    status = Column(Enum(PostStatus), nullable=False, default=PostStatus.draft)
    scheduled_time = Column(DateTime(timezone=True), nullable=True)
    published_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    # Relationship
    analytics = relationship("Analytics", back_populates="post", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "platform": self.platform.value if self.platform else None,
            "caption": self.caption,
            "image_url": self.image_url,
            "status": self.status.value if self.status else None,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "published_time": self.published_time.isoformat() if self.published_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(String, primary_key=True, default=_uuid)
    post_id = Column(String, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    engagement = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    fetched_at = Column(DateTime(timezone=True), default=_utcnow)

    # Relationship
    post = relationship("Post", back_populates="analytics")

    def to_dict(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "reach": self.reach,
            "impressions": self.impressions,
            "engagement": self.engagement,
            "engagement_rate": self.engagement_rate,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }
