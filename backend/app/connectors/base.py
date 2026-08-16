from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.document import ForumDocument

class BaseConnector(ABC):
    """
    Abstract Base Class for all forum connectors.
    Every connector MUST implement these methods.
    """

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[ForumDocument]:
        """
        Query the external forum API and return normalized documents.
        """
        pass

    @abstractmethod
    async def get_document(self, external_id: str) -> Optional[ForumDocument]:
        """
        Fetch a specific document by its external platform ID.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verify that the forum API is reachable and credentials (if any) are valid.
        """
        pass