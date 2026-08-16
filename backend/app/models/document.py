import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, JSON, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base
from app.schemas.document import ForumType, ContentType

class DBForumDocument(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String, index=True)
    forum: Mapped[ForumType] = mapped_column(SQLEnum(ForumType))
    forum_name: Mapped[str] = mapped_column(String)
    community: Mapped[str] = mapped_column(String, index=True)
    content_type: Mapped[ContentType] = mapped_column(SQLEnum(ContentType))
    title: Mapped[str] = mapped_column(String, nullable=True)
    body: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    answer_count: Mapped[int] = mapped_column(Integer, default=0)
    accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Store tags as a JSON array natively in Postgres
    tags: Mapped[list] = mapped_column(JSON, default=list)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)