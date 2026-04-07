import React from 'react';
import { Shield, Activity, Zap } from 'lucide-react';

export default function Header({ running, done, totalReward, stepNum }) {
  return (
    <header style={{
      padding: '16px 24px',
      borderBottom: '1px solid var(--border)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      background: 'linear-gradient(180deg, rgba(13,21,38,0.95) 0%, transparent 100%)',
      backdropFilter: 'blur(20px)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{
          width: 40, height: 40,
          background: 'linear-gradient(135deg, #00e5ff22, #0077ff33)',
          border: '1px solid rgba(0,229,255,0.4)',
          borderRadius: 10,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Shield size={20} color="var(--accent-cyan)" />
        </div>
        <div>
          <div style={{ fontFamily: 'Syne', fontWeight: 800, fontSize: 18, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
            Truth<span style={{ color: 'var(--accent-cyan)' }}>Guard</span>
            <span style={{ fontSize: 11, fontWeight: 400, color: 'var(--text-dim)', marginLeft: 8, fontFamily: 'JetBrains Mono', letterSpacing: 0 }}>v1.0</span>
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono', marginTop: 1 }}>
            AI Product Safety Auditor
          </div>
        </div>
      </div>

      {/* Status indicators */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
        <Stat label="STEP" value={stepNum} color="var(--accent-cyan)" icon={<Activity size={12} />} />
        <Stat label="REWARD" value={totalReward.toFixed(3)} color={totalReward >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'} icon={<Zap size={12} />} />

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 8, height: 8, borderRadius: '50%',
            background: done ? 'var(--accent-amber)' : running ? 'var(--accent-green)' : 'var(--text-dim)',
            boxShadow: running ? '0 0 12px var(--accent-green)' : done ? '0 0 12px var(--accent-amber)' : 'none',
            transition: 'all 0.3s',
            animation: running ? 'pulse-glow 1.5s ease-in-out infinite' : 'none',
          }} />
          <span style={{ fontSize: 11, fontFamily: 'JetBrains Mono', color: 'var(--text-secondary)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
            {done ? 'Complete' : running ? 'Running' : 'Idle'}
          </span>
        </div>

        {/* OpenEnv badge */}
        <div className="badge badge-purple">OpenEnv</div>
      </div>
    </header>
  );
}

function Stat({ label, value, color, icon }) {
  return (
    <div style={{ textAlign: 'right' }}>
      <div style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono', letterSpacing: '0.1em', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: 4, justifyContent: 'flex-end' }}>
        {icon}{label}
      </div>
      <div style={{ fontSize: 18, fontFamily: 'JetBrains Mono', fontWeight: 700, color, transition: 'color 0.3s' }}>{value}</div>
    </div>
  );
}
