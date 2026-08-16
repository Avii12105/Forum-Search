import { useEffect, useState } from 'react';
import apiClient from '../services/api';

export default function Home() {
  const [healthData, setHealthData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Fetch data from the FastAPI /health endpoint
    const checkHealth = async () => {
      try {
        const response = await apiClient.get('/health');
        setHealthData(response.data);
      } catch (err) {
        setError('Failed to connect to the backend. Is FastAPI running?');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
  }, []);

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>ForumSearch Engine</h1>
      
      <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ccc', borderRadius: '8px' }}>
        <h2>Backend Connectivity Status</h2>
        
        {loading && <p>Connecting to FastAPI...</p>}
        
        {error && <p style={{ color: 'red' }}>{error}</p>}
        
        {healthData && (
          <>
            <p style={{ color: 'green', fontWeight: 'bold' }}>✅ Connected successfully!</p>
            <pre style={{ background: '#f4f4f4', padding: '1rem', borderRadius: '4px' }}>
              {JSON.stringify(healthData, null, 2)}
            </pre>
          </>
        )}
      </div>
    </div>
  );
}