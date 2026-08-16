import logging
from typing import List, Dict
import chromadb

from app.schemas.document import ForumDocument

logger = logging.getLogger(__name__)

class VectorService:
    """
    Manages semantic vector embeddings using a local ChromaDB instance.
    Automatically handles tokenization and embedding generation using ONNX.
    """
    def __init__(self):
        # Creates a local database folder named 'chroma_db' in your backend directory
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Get or create our document collection
        self.collection = self.client.get_or_create_collection(
            name="forum_documents",
            metadata={"hnsw:space": "cosine"} # Use cosine similarity for semantic distance
        )
        logger.info("ChromaDB Vector Store initialized.")

    def upsert_documents(self, documents: List[ForumDocument]):
        """
        Converts text to vectors and stores them in ChromaDB.
        """
        if not documents:
            return
            
        docs = []
        metadatas = []
        ids = []

        for doc in documents:
            # We embed both the title and a snippet of the body for rich context
            semantic_text = f"{doc.title}. {doc.body[:500]}"
            docs.append(semantic_text)
            
            # Store metadata so we can trace the vector back to the source
            metadatas.append({
                "forum": doc.forum,
                "url": doc.url,
                "score": doc.score
            })
            ids.append(doc.external_id)

        try:
            self.collection.upsert(
                documents=docs,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Upserted {len(documents)} documents into vector store.")
        except Exception as e:
            logger.error(f"Vector DB upsert failed: {e}")

    def semantic_search(self, query: str, n_results: int = 50) -> Dict[str, float]:
        """
        Searches the vector space and returns a dictionary mapping 
        external_ids to their semantic similarity score (1.0 is perfect match).
        """
        try:
            # Tell Chroma to return 'distances' alongside the documents
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["distances"]
            )
            
            if not results['ids'] or len(results['ids'][0]) == 0:
                return {}
                
            ids = results['ids'][0]
            distances = results['distances'][0]
            
            similarity_scores = {}
            for doc_id, dist in zip(ids, distances):
                # Maximize at 1.0, minimize at 0.0
                similarity_scores[doc_id] = max(0.0, 1.0 - dist)
                
            return similarity_scores
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return {}