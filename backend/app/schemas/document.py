from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict

class ForumType(str, Enum):
    """Supported platform identifiers."""
    STACKOVERFLOW = "stackoverflow"
    STACKEXCHANGE = "stackexchange"
    HACKERNEWS = "hackernews"
    DISCOURSE = "discourse"
    LEMMY = "lemmy"
    GITHUB = "github"

class ContentType(str, Enum):
    """Standardized content types across all platforms."""
    QUESTION = "question"
    ANSWER = "answer"
    DISCUSSION = "discussion"
    COMMENT = "comment"

class ForumDocument(BaseModel):
    """
    The Canonical Document Model.
    All external API data MUST be mapped to this structure.
    """
    id: UUID = Field(default_factory=uuid4, description="Internal unique identifier")
    external_id: str = Field(..., description="ID from the source platform")
    forum: ForumType = Field(..., description="Platform identifier")
    forum_name: str = Field(..., description="Human-readable platform name")
    community: str = Field(..., description="Subreddit, SO site, or repository")
    content_type: ContentType = Field(..., description="Type of content")
    title: Optional[str] = Field(None, description="Post title (Null for comments/answers)")
    body: str = Field(..., description="Main textual content")
    author: str = Field(..., description="Username of the creator")
    url: str = Field(..., description="Canonical URL to the post")
    created_at: datetime = Field(..., description="Timestamp of creation (UTC)")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of last edit (UTC)")
    score: int = Field(default=0, description="Net upvotes/downvotes")
    comment_count: int = Field(default=0, description="Number of child comments")
    answer_count: int = Field(default=0, description="Number of answers (if applicable)")
    accepted: bool = Field(default=False, description="True if marked as the accepted solution")
    tags: List[str] = Field(default_factory=list, description="Associated topics")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible platform-specific data")

    # V2 Config: Allows Pydantic to read data directly from SQLAlchemy ORM models later
    model_config = ConfigDict(from_attributes=True)