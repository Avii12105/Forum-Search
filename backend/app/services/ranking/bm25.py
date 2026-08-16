import math
import re
from collections import defaultdict, Counter
from typing import List, Dict

from app.schemas.document import ForumDocument

class BM25Engine:
    """
    In-memory Okapi BM25 scorer for re-ranking federated search results.
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
    
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        if not text:
            return []
        return re.findall(r'\b\w+\b', text.lower())

    def rank(self, query: str, documents: List[ForumDocument]) -> Dict[str, float]:
        """
        Calculates BM25 scores for a list of documents against a query.
        """
        if not documents or not query:
            return {doc.external_id: 0.0 for doc in documents}
            
        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return {doc.external_id: 0.0 for doc in documents}

        N = len(documents)
        doc_tokens_map = {}
        df = defaultdict(int) 
        
        total_length = 0

        # 1. Tokenize corpus, calculate Document Frequencies (DF), and find average length
        for doc in documents:
            text = f"{doc.title} {doc.body}"
            tokens = self._tokenize(text)
            doc_tokens_map[doc.external_id] = tokens
            
            total_length += len(tokens)
            
            unique_tokens = set(tokens)
            for token in unique_tokens:
                df[token] += 1

        avgdl = total_length / N if N > 0 else 0

        # 2. Calculate BM25 scores
        scores = {}
        for doc in documents:
            tokens = doc_tokens_map[doc.external_id]
            doc_len = len(tokens)
            
            if doc_len == 0:
                scores[doc.external_id] = 0.0
                continue
                
            token_counts = Counter(tokens)
            doc_score = 0.0
            
            for q_token in query_tokens:
                if q_token in token_counts:
                    f_q_D = token_counts[q_token]
                    n_q = df[q_token]
                    
                    # IDF component
                    idf = math.log(((N - n_q + 0.5) / (n_q + 0.5)) + 1.0)
                    
                    # TF component with length normalization
                    numerator = f_q_D * (self.k1 + 1)
                    denominator = f_q_D + self.k1 * (1 - self.b + self.b * (doc_len / avgdl))
                    
                    doc_score += idf * (numerator / denominator)
                    
            scores[doc.external_id] = doc_score
            
        return scores