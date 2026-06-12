import { useEffect, useState } from 'react';

export default function Home() {
  const [svgUrl, setSvgUrl] = useState('');

  useEffect(() => {
    setSvgUrl('/api/svg');
  }, []);

  return (
    <div style={{
      minHeight: '100vh',
      background: '#0d1117',
      color: '#e6edf3',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '40px 20px'
    }}>
      <h1 style={{ fontSize: '32px', marginBottom: '10px' }}>
        AI Coding Blue Wall
      </h1>
      <p style={{ color: '#8b949e', marginBottom: '40px', textAlign: 'center' }}>
        Track your token usage across Codex, Claude Code, MimoCode, and more
      </p>

      <div style={{
        background: '#161b22',
        borderRadius: '8px',
        padding: '20px',
        maxWidth: '900px',
        width: '100%'
      }}>
        {svgUrl && <img src={svgUrl} alt="AI Coding Blue Wall" style={{ width: '100%' }} />}
      </div>

      <div style={{ marginTop: '40px', textAlign: 'center' }}>
        <h2 style={{ fontSize: '20px', marginBottom: '20px' }}>Embed in GitHub Profile</h2>
        <pre style={{
          background: '#161b22',
          padding: '15px',
          borderRadius: '6px',
          overflow: 'auto',
          maxWidth: '600px'
        }}>
          <code>{`## AI Coding Activity

<picture>
  <source media="(prefers-color-scheme: dark)" 
    srcset="${typeof window !== 'undefined' ? window.location.origin : ''}/api/svg">
  <img alt="AI Coding Blue Wall" 
    src="${typeof window !== 'undefined' ? window.location.origin : ''}/api/svg">
</picture>`}</code>
        </pre>
      </div>

      <div style={{ marginTop: '40px', textAlign: 'center', color: '#8b949e' }}>
        <p>Data updates every hour from GitHub</p>
        <p>Supports: Codex | Claude Code | MimoCode</p>
      </div>
    </div>
  );
}
