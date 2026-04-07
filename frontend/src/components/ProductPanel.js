import React from 'react';
import { Package, Tag, AlertTriangle, CheckCircle } from 'lucide-react';

export default function ProductPanel({ obs, state }) {
  if (!obs) return <div className="card" style={{ padding: 20, color: 'var(--text-dim)', fontSize: 13 }}>No product loaded</div>;

  const harmfulKws = ['parabens','formaldehyde','lead','mercury','oxybenzone','bpa','phthalates','triclosan','sodium lauryl sulfate','propylene glycol','diethanolamine','petrolatum','aluminum','talc','synthetic fragrance'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {/* Product info */}
      <div className="card" style={{ padding: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <Package size={14} color="var(--accent-cyan)" />
          <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-secondary)', letterSpacing: '0.1em', textTransform: 'uppercase', fontFamily: 'JetBrains Mono' }}>Product</span>
        </div>
        <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4, lineHeight: 1.3 }}>{obs.product_name}</div>
        <div className="badge badge-cyan" style={{ marginBottom: 12 }}>{obs.product_category}</div>
        
        <div style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8 }}>Label Claims</div>
        {obs.label_claims?.map((c, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, fontSize: 12, color: obs.checked_claims?.[c] === false ? 'var(--accent-red)' : obs.checked_claims?.[c] === true ? 'var(--accent-green)' : 'var(--text-secondary)' }}>
            {obs.checked_claims?.[c] === false ? <AlertTriangle size={11} /> : obs.checked_claims?.[c] === true ? <CheckCircle size={11} /> : <Tag size={11} />}
            {c}
          </div>
        ))}
      </div>

      {/* Known ingredients */}
      <div className="card" style={{ padding: 16 }}>
        <div style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>
          Discovered ({obs.visible_ingredients?.length || 0})
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 280, overflowY: 'auto' }}>
          {obs.visible_ingredients?.map((ing, i) => {
            const isHarmful = harmfulKws.some(k => ing.includes(k));
            return (
              <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '5px 8px', borderRadius: 6, background: isHarmful ? 'rgba(255,61,110,0.08)' : 'rgba(0,255,157,0.05)', border: `1px solid ${isHarmful ? 'rgba(255,61,110,0.2)' : 'rgba(0,255,157,0.1)'}` }}>
                <span style={{ fontSize: 11, fontFamily: 'JetBrains Mono', color: isHarmful ? 'var(--accent-red)' : 'var(--text-primary)' }}>{ing}</span>
                {isHarmful && <span style={{ fontSize: 9, color: 'var(--accent-red)', fontWeight: 700 }}>⚠</span>}
              </div>
            );
          })}
          {(!obs.visible_ingredients || obs.visible_ingredients.length === 0) && (
            <div style={{ fontSize: 12, color: 'var(--text-dim)' }}>No ingredients discovered yet</div>
          )}
        </div>
      </div>
    </div>
  );
}
