import React, { useState, useRef } from 'react';
import { Upload, Image, CheckCircle, AlertCircle, Loader } from 'lucide-react';

const API = process.env.REACT_APP_API_URL || '';

export default function ImageUpload({ onProductExtracted, difficulty }) {
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [extracted, setExtracted] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef();

  const handleFile = async (file) => {
    if (!file) return;
    setError(null);
    setLoading(true);
    setPreview(URL.createObjectURL(file));

    const formData = new FormData();
    formData.append('file', file);
    formData.append('difficulty', difficulty);

    try {
      const r = await fetch(`${API}/upload_image`, { method: 'POST', body: formData });
      const d = await r.json();
      if (d.success) {
        setExtracted(d.product_data);
        onProductExtracted(d.product_data);
      } else {
        setError('Extraction failed');
      }
    } catch (e) {
      setError('Upload failed: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 16, alignItems: 'center' }}>
      {/* Upload zone */}
      <div
        className="card"
        onDrop={onDrop}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onClick={() => inputRef.current?.click()}
        style={{
          padding: '16px 20px',
          cursor: 'pointer',
          border: `1px solid ${dragging ? 'var(--accent-cyan)' : error ? 'var(--accent-red)' : extracted ? 'var(--accent-green)' : 'var(--border)'}`,
          transition: 'all 0.25s',
          boxShadow: dragging ? 'var(--glow-cyan)' : extracted ? 'var(--glow-green)' : 'none',
          display: 'flex',
          alignItems: 'center',
          gap: 16,
        }}
      >
        <input ref={inputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={e => handleFile(e.target.files[0])} />

        {/* Preview / icon */}
        {preview ? (
          <img src={preview} alt="product" style={{ width: 52, height: 52, objectFit: 'cover', borderRadius: 8, border: '1px solid var(--border-bright)' }} />
        ) : (
          <div style={{
            width: 52, height: 52, borderRadius: 8,
            background: 'var(--bg-deep)',
            border: '1px dashed var(--border-bright)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            {loading ? <Loader size={20} color="var(--accent-cyan)" style={{ animation: 'spin-slow 1s linear infinite' }} /> : <Upload size={20} color="var(--text-dim)" />}
          </div>
        )}

        <div style={{ flex: 1 }}>
          {extracted ? (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <CheckCircle size={14} color="var(--accent-green)" />
                <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--accent-green)' }}>Product Extracted</span>
              </div>
              <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{extracted.product_name}</div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono' }}>
                {extracted.category} · {extracted.ingredients?.length} ingredients · {difficulty}
              </div>
            </div>
          ) : error ? (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <AlertCircle size={14} color="var(--accent-red)" />
                <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--accent-red)' }}>Error</span>
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{error}</div>
            </div>
          ) : (
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Image size={14} color="var(--accent-cyan)" />
                  Upload Product Image
                </span>
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-dim)' }}>
                Drop an image or click to browse · JPG, PNG, WEBP supported
              </div>
            </div>
          )}
        </div>

        {loading && (
          <div style={{ fontSize: 11, color: 'var(--accent-cyan)', fontFamily: 'JetBrains Mono' }}>
            Extracting…
          </div>
        )}
      </div>

      {/* Info tag */}
      <div style={{ textAlign: 'center', padding: '8px 16px', background: 'var(--bg-card)', borderRadius: 8, border: '1px solid var(--border)' }}>
        <div style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Mode</div>
        <div style={{ fontSize: 20, fontWeight: 800, color: difficulty === 'easy' ? 'var(--accent-green)' : difficulty === 'medium' ? 'var(--accent-amber)' : 'var(--accent-red)', fontFamily: 'Syne', marginTop: 2 }}>
          {difficulty.toUpperCase()}
        </div>
      </div>
    </div>
  );
}
