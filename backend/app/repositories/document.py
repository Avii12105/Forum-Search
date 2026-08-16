import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.document import DBForumDocument
from app.schemas.document import ForumDocument

logger = logging.getLogger(__name__)

class DocumentRepository:
    """
    Repository layer for managing DBForumDocument persistence in PostgreSQL.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upsert_documents(self, documents: List[ForumDocument]) -> int:
        """
        Persists a list of canonical ForumDocument Pydantic models to PostgreSQL.
        Updates existing entries if external_id and forum match; inserts new ones otherwise.
        """
        if not documents:
            return 0

        saved_count = 0
        try:
            for doc in documents:
                # Query for existing record matching both external_id and forum platform
                stmt = select(DBForumDocument).where(
                    DBForumDocument.external_id == doc.external_id,
                    DBForumDocument.forum == doc.forum
                )
                result = await self.db.execute(stmt)
                existing_doc = result.scalars().first()

                if existing_doc:
                    # Update dynamic stats/content
                    existing_doc.title = doc.title
                    existing_doc.body = doc.body
                    existing_doc.score = doc.score
                    existing_doc.comment_count = doc.comment_count
                    existing_doc.answer_count = doc.answer_count
                    existing_doc.accepted = doc.accepted
                    existing_doc.updated_at = doc.updated_at
                    existing_doc.tags = doc.tags
                    existing_doc.metadata_json = doc.metadata
                else:
                    # Create new ORM record
                    db_doc = DBForumDocument(
                        id=doc.id,
                        external_id=doc.external_id,
                        forum=doc.forum,
                        forum_name=doc.forum_name,
                        community=doc.community,
                        content_type=doc.content_type,
                        title=doc.title,
                        body=doc.body,
                        author=doc.author,
                        url=doc.url,
                        created_at=doc.created_at,
                        updated_at=doc.updated_at,
                        score=doc.score,
                        comment_count=doc.comment_count,
                        answer_count=doc.answer_count,
                        accepted=doc.accepted,
                        tags=doc.tags,
                        metadata_json=doc.metadata
                    )
                    self.db.add(db_doc)
                    saved_count += 1

            await self.db.commit()
            logger.info(f"Persisted {len(documents)} documents to Postgres ({saved_count} new).")
            return saved_count

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to persist documents to PostgreSQL: {str(e)}")
            return 0

    async def get_autocomplete_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """
        Fetches distinct document titles from PostgreSQL that contain the query string.
        """
        if not query or len(query) < 2:
            return []
            
        try:
            # Case-insensitive search anywhere in the title
            stmt = (
                select(DBForumDocument.title)
                .where(DBForumDocument.title.ilike(f"%{query}%"))
                .distinct()
                .limit(limit)
            )
            result = await self.db.execute(stmt)
            # scalars().all() extracts the first column (title) into a flat list of strings
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Failed to fetch autocomplete suggestions: {str(e)}")
            return []