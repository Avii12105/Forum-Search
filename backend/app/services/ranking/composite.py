import math
from datetime import datetime, timezone
from typing import List, Dict

from app.schemas.document import ForumDocument
from app.services.ranking.bm25 import BM25Engine

class CompositeRanker:
    def __init__(self):
        self.bm25_engine = BM25Engine()
        
    def rank(self, query: str, documents: List[ForumDocument], semantic_scores: Dict[str, float] = None) -> Dict[str, float]:
        if not documents:
            return {}
            
        semantic_scores = semantic_scores or {}
        bm25_scores = self.bm25_engine.rank(query, documents)
        now = datetime.now(timezone.utc)
        
        # 1. Normalize BM25 scores so they are roughly on the same scale as Semantic Scores (0 to 1)
        max_bm25 = max(bm25_scores.values()) if bm25_scores.values() else 1.0
        if max_bm25 == 0: 
            max_bm25 = 1.0
        
        composite_scores = {}
        
        for doc in documents:
            # --- HYBRID TEXT RELEVANCE ---
            normalized_bm25 = bm25_scores.get(doc.external_id, 0.0) / max_bm25
            semantic_similarity = semantic_scores.get(doc.external_id, 0.0)
            
            # Weighting: 60% AI Semantic Meaning, 40% Exact Keyword Match
            hybrid_text_score = (semantic_similarity * 0.6) + (normalized_bm25 * 0.4)
            
            # --- COMMUNITY METADATA ---
            safe_score = max(0, doc.score)
            community_bonus = math.log10(safe_score + 1) * 1.5  # Scaled down to fit new 0-1 text bounds
            accepted_bonus = 0.5 if doc.accepted else 0.0
            
            # --- RECENCY DECAY ---
            days_old = max(0, (now - doc.created_at).days)
            time_decay = max(0.5, 1.0 - (days_old / 7300))
            
            # Final formula combines the hybrid text understanding with community trust
            final_score = (hybrid_text_score + community_bonus + accepted_bonus) * time_decay
            
            composite_scores[doc.external_id] = final_score
            
        return composite_scores