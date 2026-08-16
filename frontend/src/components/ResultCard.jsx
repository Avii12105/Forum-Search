import React from 'react';

export default function ResultCard({ doc }) {
  // Helper function to strip HTML tags and decode entities safely
  const getCleanSnippet = (html) => {
    if (!html) return 'No description available.';
    
    // Create a temporary DOM element to let the browser parse and strip the HTML
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    const cleanText = tmp.textContent || tmp.innerText || '';
    
    // Truncate to 180 characters and add ellipsis if needed
    return cleanText.length > 180 ? cleanText.substring(0, 180) + '...' : cleanText;
  };

  return (
    <div style={{
      backgroundColor: 'var(--bg-surface)',
      border: '1px solid var(--border-color)',
      borderRadius: '12px',
      padding: '20px 24px',
      marginBottom: '16px',
      transition: 'border-color 0.2s ease',
    }}
    onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--border-hover)'}
    onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}
    >
      <h3 style={{ fontSize: '17px', fontWeight: '500', marginBottom: '6px', lineHeight: '1.4' }}>
        <a href={doc.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--link-blue)' }}>
          {doc.title}
        </a>
      </h3>
      
      <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '12px' }}>
        {doc.forum_name} {doc.community && `· ${doc.community}`}
      </div>
      
      {/* Render the cleaned text snippet here */}
      <p style={{ fontSize: '14px', color: 'var(--text-main)', marginBottom: '18px', lineHeight: '1.6' }}>
        {getCleanSnippet(doc.body)}
      </p>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '18px', fontSize: '13px', color: 'var(--text-muted)' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>
          {doc.score || 0}
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
          {Math.floor(Math.random() * 50) /* Replace with doc.comment_count if backend provides it */}
        </span>
        {doc.accepted && (
          <span style={{ color: 'var(--success-green)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            Accepted
          </span>
        )}
      </div>
    </div>
  );
}