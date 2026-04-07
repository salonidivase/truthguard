import React from 'react';
import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts';
import { Brain, Eye, Shield, Target } from 'lucide-react';

export default function BeliefPanel({ obs, state, running }) {
  const risk = obs?.risk_estimate || 0;
  const confidence = obs?.confidence || 0;
  const riskColor = risk < 0.3 ? 'var(--accent-green)' : risk < 0.6 ? 'var(--accent-amber)' : 'var(--accent-red)';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {/* Risk gauge */}
      <div className="card" style={{ padding: 16, textAlign: 'center' }}>
        <div style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6, justifyContent: 'center' }}>
          <Shield size={11} /> Risk Score
        </div>
        <div style={{ position: 'relative', height: 140 }}>
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart cx="50%" cy="75%" innerRadius="60%" outerRadius="90%" startAngle={180} endAngle={0} data={[{ value: risk * 100, fill: riskColor }]}>
              <RadialBar dataKey="value" cornerRadius={4} />
            </RadialBarChart>
          </ResponsiveContainer>
          <div style={{ position: 'absolute', bottom: 8, left: '50%', transform: 'translateX(-50%)', textAlign: 'center' }}>
            <div style={{ fontSize: 28, fontWeight: 800, fontFamily: 'JetBrains Mono', color: riskColor }}>{(risk * 100).toFixed(0)}<span style={{ fontSize: 14 }}>%</span></div>
            <div style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono' }}>
              {risk < 0.3 ? 'LOW RISK' : risk < 0.6 ? 'MODERATE' : 'HIGH RISK'}
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="card" style={{ padding: 16 }}>
        <StatRow icon={<Eye size={12} />} label="Confidence" value={`${(confidence * 100).toFixed(0)}%`} bar={confidence} color="var(--accent-cyan)" />
        <StatRow icon={<Brain size={12} />} label="Known Ingredients" value={obs?.visible_ingredients?.length || 0} bar={obs?.visible_ingredients?.length ? obs.visible_ingredients.length / 15 : 0} color="var(--accent-purple)" />
        <StatRow icon={<Target size={12} />} label="Claims Verified" value={Object.keys(obs?.checked_claims || {}).length} bar={obs?.label_claims?.length ? Object.keys(obs?.checked_claims || {}).length / obs.label_claims.length : 0} color="var(--accent-green)" />
      </div>

      {/* True risk (hidden) reveal */}
      {state && (
        <div className="card" style={{ padding: 16 }}>
          <div style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>Ground Truth</div>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginBottom: 6 }}>
            True Risk: <span style={{ color: state.true_risk_score >= 0.5 ? 'var(--accent-red)' : 'var(--accent-green)', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>{(state.true_risk_score * 100).toFixed(0)}%</span>
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginBottom: 6 }}>
            Harmful: <span style={{ color: 'var(--accent-amber)', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>{Object.values(state.harmful_flags || {}).filter(Boolean).length}</span> ingredients
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
            Difficulty: <span className={`badge badge-${state.difficulty === 'easy' ? 'green' : state.difficulty === 'medium' ? 'amber' : 'red'}`}>{state.difficulty}</span>
          </div>
        </div>
      )}
    </div>
  );
}

function StatRow({ icon, label, value, bar, color }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'var(--text-secondary)' }}>{icon}{label}</div>
        <div style={{ fontFamily: 'JetBrains Mono', fontSize: 13, fontWeight: 700, color }}>{value}</div>
      </div>
      <div className="progress-bar-track">
        <div className="progress-bar-fill" style={{ width: `${Math.min(bar * 100, 100)}%`, background: color }} />
      </div>
    </div>
  );
}
