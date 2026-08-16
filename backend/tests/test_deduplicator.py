from datetime import datetime, timezone
from app.schemas.document import ForumDocument, ForumType, ContentType
from app.services.deduplicator import Deduplicator

def test_deduplicator_removes_exact_urls():
    # Arrange: Create two fake documents pointing to the exact same URL
    doc1 = ForumDocument(
        external_id="1",
        forum=ForumType.STACKEXCHANGE,
        forum_name="Stack Overflow",
        community="tech",
        content_type=ContentType.QUESTION,
        title="Test 1",
        body="Body 1",
        author="UserA",
        url="https://example.com/post/123",
        created_at=datetime.now(timezone.utc),
        score=100  # Higher score
    )
    
    doc2 = ForumDocument(
        external_id="2",
        forum=ForumType.HACKERNEWS,
        forum_name="Hacker News",
        community="tech",
        content_type=ContentType.DISCUSSION,
        title="Test 2",
        body="Body 2",
        author="UserB",
        url="https://example.com/post/123",
        created_at=datetime.now(timezone.utc),
        score=50   # Lower score
    )
    
    deduplicator = Deduplicator()
    
    # Act: Pass both documents through the deduplicator
    results = deduplicator.deduplicate([doc1, doc2])
    
    # Assert: Only 1 document should remain, and it should be the one with the higher score
    assert len(results) == 1
    assert results[0].external_id == "1"
    assert results[0].score == 100