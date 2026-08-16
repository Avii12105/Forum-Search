import React from 'react';

export default function LoadingSkeleton() {
  const skeletons = [1, 2, 3, 4, 5];

  const shimmerStyle = {
    background: 'linear-gradient(90deg, #1A1F29 25%, #232936 50%, #1A1F29 75%)',
    backgroundSize: '1000px 100%',
    animation: 'shimmer 2s infinite linear',
    borderRadius: '4px'
  };

  return (
    <div style={{ width: '100%' }}>
      <h2 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '24px', color: 'var(--text-main)' }}>
        Search Results
      </h2>
      {skeletons.map((i) => (
        <div key={i} style={{
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-color)',
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '16px'
        }}>
          <div style={{ height: '20px', width: '85%', marginBottom: '16px', ...shimmerStyle }}></div>
          <div style={{ height: '14px', width: '25%', marginBottom: '24px', ...shimmerStyle }}></div>
          <div style={{ height: '14px', width: '100%', marginBottom: '10px', ...shimmerStyle }}></div>
          <div style={{ height: '14px', width: '90%', marginBottom: '10px', ...shimmerStyle }}></div>
          <div style={{ height: '14px', width: '60%', ...shimmerStyle }}></div>
        </div>
      ))}
    </div>
  );
}