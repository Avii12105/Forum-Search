import React, { useState, useEffect } from 'react';
import './index.css';
import SearchBar from './components/SearchBar';
import ResultCard from './components/ResultCard';
import LoadingSkeleton from './components/LoadingSkeleton';

function App() {
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState(false);
  const [acceptedOnly, setAcceptedOnly] = useState(false);
  
  // --- NEW: Pagination State ---
  const [currentPage, setCurrentPage] = useState(1);
  const RESULTS_PER_PAGE = 10;

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const initialQuery = params.get('q');
    const initialAccepted = params.get('accepted') === 'true';
    
    if (initialAccepted) setAcceptedOnly(true);

    if (initialQuery) {
      executeSearch(initialQuery, initialAccepted);
    }
  }, []);

  const executeSearch = async (searchQuery, isAccepted = acceptedOnly) => {
    if (!searchQuery.trim()) return;
    
    const url = new URL(window.location);
    url.searchParams.set('q', searchQuery);
    
    if (isAccepted) {
      url.searchParams.set('accepted', 'true');
    } else {
      url.searchParams.delete('accepted');
    }
    window.history.pushState({}, '', url);

    setIsSearching(true);
    setHasSearched(true);
    setError(false);
    setCurrentPage(1); // Reset to page 1 on new search
    
    try {
      let apiUrl = `http://localhost:8000/api/search?q=${encodeURIComponent(searchQuery)}&limit=15`;
      if (isAccepted) apiUrl += `&accepted_only=true`;

      const response = await fetch(apiUrl);
      if (!response.ok) throw new Error("Search failed");
      const data = await response.json();
      setResults(data);
    } catch (err) {
      console.error("Search API Error:", err);
      setError(true);
      setResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleToggleAccepted = () => {
    const newValue = !acceptedOnly;
    setAcceptedOnly(newValue);
    
    const currentQuery = new URLSearchParams(window.location.search).get('q');
    if (currentQuery) {
      executeSearch(currentQuery, newValue);
    }
  };

  const handleGoHome = () => {
    setHasSearched(false);
    setResults([]);
    setIsSearching(false);
    setError(false);
    setAcceptedOnly(false);
    setCurrentPage(1);
    window.history.pushState({}, '', window.location.pathname);
  };

  // --- NEW: Pagination Logic ---
  const totalPages = Math.ceil(results.length / RESULTS_PER_PAGE);
  const currentResults = results.slice(
    (currentPage - 1) * RESULTS_PER_PAGE,
    currentPage * RESULTS_PER_PAGE
  );

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
      window.scrollTo({ top: 0, behavior: 'smooth' }); // Scroll to top on page change
    }
  };

  // Generate dynamic page numbers (showing max 5 pages around the current page)
  const getPageNumbers = () => {
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    
    if (endPage - startPage < 4) {
      startPage = Math.max(1, endPage - 4);
    }

    const pages = [];
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    return pages;
  };

  const LogoIcon = () => (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '8px' }}>
      <path d="M12 2L14.2 9.8L22 12L14.2 14.2L12 22L9.8 14.2L2 12L9.8 9.8L12 2Z" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
    </svg>
  );

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {hasSearched && (
        <header style={{ padding: '24px 32px', width: '100%', maxWidth: '960px', margin: '0 auto' }}>
          <div 
            onClick={handleGoHome}
            style={{ 
              fontWeight: '600', 
              fontSize: '20px', 
              color: 'var(--text-main)', 
              display: 'inline-flex', 
              alignItems: 'center',
              cursor: 'pointer' 
            }}
          >
            <LogoIcon /> ForumSearch
          </div>
        </header>
      )}

      <main style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center',
        padding: hasSearched ? '10px 24px 80px 24px' : '22vh 24px 24px 24px',
        width: '100%',
        maxWidth: '960px',
        margin: '0 auto'
      }}>
        
        {!hasSearched && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', maxWidth: '700px' }}>
            <div 
              onClick={handleGoHome}
              style={{ fontWeight: '700', fontSize: '40px', color: 'var(--text-main)', display: 'flex', alignItems: 'center', marginBottom: '8px', cursor: 'pointer' }}
            >
              <LogoIcon /> ForumSearch
            </div>
            <h2 style={{ fontSize: '18px', fontWeight: '400', marginBottom: '32px', color: 'var(--text-muted)' }}>
              Search community knowledge
            </h2>
            
            <SearchBar initialQuery={new URLSearchParams(window.location.search).get('q')} onExecuteSearch={(q) => executeSearch(q, acceptedOnly)} />
            
            <div style={{ marginTop: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
              Stack Overflow · Stack Exchange · Hacker News · Discourse · Lemmy · GitHub Discussions
            </div>
          </div>
        )}

        {hasSearched && (
          <div style={{ width: '100%', maxWidth: '800px' }}>
            <div style={{ marginBottom: '32px' }}>
              <SearchBar initialQuery={new URLSearchParams(window.location.search).get('q')} onExecuteSearch={(q) => executeSearch(q, acceptedOnly)} />
            </div>
            
            {!isSearching && !error && results.length > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <span style={{ fontSize: '15px', fontWeight: '500' }}>{results.length} results</span>
                
                <button 
                  onClick={handleToggleAccepted}
                  style={{ 
                    backgroundColor: acceptedOnly ? 'rgba(63, 185, 80, 0.1)' : 'var(--bg-input)', 
                    border: `1px solid ${acceptedOnly ? 'rgba(63, 185, 80, 0.4)' : 'var(--border-color)'}`, 
                    color: acceptedOnly ? 'var(--success-green)' : 'var(--text-main)', 
                    padding: '6px 12px', 
                    borderRadius: '6px', 
                    fontSize: '13px', 
                    cursor: 'pointer', 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '6px',
                    transition: 'all 0.2s ease'
                  }}>
                  {acceptedOnly && (
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  )}
                  Accepted Only
                </button>
              </div>
            )}

            {error && (
              <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                Some sources could not be searched. Please try again.
              </div>
            )}

            {isSearching && <LoadingSkeleton />}

            {!isSearching && !error && results.length > 0 && (
              <div>
                {/* --- RENDER CURRENT PAGE RESULTS --- */}
                {currentResults.map((doc) => (
                  <ResultCard key={doc.external_id} doc={doc} />
                ))}
                
                {/* --- DYNAMIC PAGINATION CONTROLS --- */}
                {totalPages > 1 && (
                  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px', marginTop: '40px', fontSize: '15px', color: 'var(--text-muted)' }}>
                    <span 
                      onClick={() => handlePageChange(currentPage - 1)}
                      style={{ cursor: currentPage > 1 ? 'pointer' : 'default', padding: '6px 10px', opacity: currentPage > 1 ? 1 : 0.3 }}
                    >
                      ←
                    </span>
                    
                    {getPageNumbers().map(pageNum => (
                      <span 
                        key={pageNum}
                        onClick={() => handlePageChange(pageNum)}
                        style={{ 
                          backgroundColor: currentPage === pageNum ? '#2D3342' : 'transparent', 
                          color: currentPage === pageNum ? '#58A6FF' : 'var(--link-blue)', 
                          padding: '8px 14px', 
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontWeight: currentPage === pageNum ? '600' : '400',
                          transition: 'all 0.2s ease'
                        }}
                      >
                        {pageNum}
                      </span>
                    ))}

                    <span 
                      onClick={() => handlePageChange(currentPage + 1)}
                      style={{ cursor: currentPage < totalPages ? 'pointer' : 'default', padding: '6px 10px', opacity: currentPage < totalPages ? 1 : 0.3 }}
                    >
                      →
                    </span>
                  </div>
                )}
              </div>
            )}

            {!isSearching && !error && results.length === 0 && (
              <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
                <p style={{ fontSize: '18px', marginBottom: '8px', color: 'var(--text-main)' }}>No results found</p>
                <p>Try a different search query or toggle filters.</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;