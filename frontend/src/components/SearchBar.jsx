import React, { useState, useEffect } from 'react';
import { useDebounce } from '../hooks/useDebounce';

export default function SearchBar({ initialQuery, onExecuteSearch }) {
  const [query, setQuery] = useState(initialQuery || '');
  const [suggestions, setSuggestions] = useState([]);
  const [isDropdownVisible, setDropdownVisible] = useState(false);
  
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery.length >= 2) {
      fetch(`http://localhost:8000/api/autocomplete?q=${encodeURIComponent(debouncedQuery)}`)
        .then(res => res.json())
        .then(data => {
          setSuggestions(data);
          setDropdownVisible(data.length > 0);
        })
        .catch(() => setSuggestions([]));
    } else {
      setSuggestions([]);
      setDropdownVisible(false);
    }
  }, [debouncedQuery]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (query.trim()) {
      setDropdownVisible(false);
      onExecuteSearch(query);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    setDropdownVisible(false);
    onExecuteSearch(suggestion);
  };

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', width: '100%' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          width: '100%',
          backgroundColor: 'var(--bg-input)',
          border: '1px solid var(--border-color)',
          borderRadius: '999px', /* Perfect pill shape */
          padding: '0 24px',
          height: '52px',
          transition: 'border-color 0.2s ease',
        }}
        onFocus={(e) => e.currentTarget.style.borderColor = 'var(--text-muted)'}
        onBlur={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '12px' }}>
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for a problem or solution"
            style={{
              flex: 1,
              backgroundColor: 'transparent',
              border: 'none',
              color: 'var(--text-main)',
              fontSize: '15px',
              outline: 'none',
              width: '100%'
            }}
          />
        </div>
      </form>
      
      {isDropdownVisible && (
        <ul style={{ 
          position: 'absolute', top: '60px', left: 0, right: 0, 
          backgroundColor: 'var(--bg-surface)', 
          border: '1px solid var(--border-color)', 
          borderRadius: '16px',
          listStyleType: 'none', padding: '8px 0', 
          boxShadow: '0 10px 30px rgba(0,0,0,0.5)', zIndex: 10
        }}>
          {suggestions.map((suggestion, index) => (
            <li 
              key={index} 
              onClick={() => handleSuggestionClick(suggestion)}
              style={{ padding: '12px 24px', cursor: 'pointer', color: 'var(--text-main)', fontSize: '15px' }}
              onMouseOver={(e) => e.target.style.backgroundColor = 'var(--bg-input)'}
              onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
            >
              {suggestion}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}