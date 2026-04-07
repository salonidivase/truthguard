import React from 'react';
import { Play, Square, RotateCcw, Bot, Shuffle, Brain } from 'lucide-react';

const AGENTS = [
  { id: 'random', label: 'Random', icon: <Shuffle size={13} />, color: 'var(--accent-amber)' },
  { id: 'rulebased', label: 'Rule-Based', icon: <Bot size={13} />, color: 'var(--accent-cyan)' },
  { id: 'smart', label: 'Smart Agent', icon: <Brain size={13} />, color: 'var(--accent-purple)' },
];

const DIFFICULTIES = [
  { id: 'easy', label: 'Easy', color: 'var(--accent-green)' },
  { id: 'medium', label: 'Medium', color: 'var(--accent-amber)' },
  { id: 'hard', label: 'Hard', color: 'var(--accent-red)' },
];

export default function ControlBar({ running, done, obs, agentType, setAgentType, seed, setSeed, difficulty, setDifficulty, onRun, onStop, onReset, isResetting }) {
  return (
    <div className="card" style={{ padding: '14px 20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 24, flexWrap: 'wrap' }}>

        {/* Agent selector */}
        <div>
          <div style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8 }}>Agent</div>
          <div style={{ display: 'flex', gap: 6 }}>
            {AGENTS.map(a => (
              <button key={a.id} onClick={() => setAgentType(a.id)} disabled={running} style={{
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '6px 14px',
                borderRadius: 6,
                border: `1px solid ${agentType === a.id ? a.color : 'var(--border)'}`,
                background: agentType === a.id ? `${a.color}18` : 'transparent',
                color: agentType === a.id ? a.color : 'var(--text-secondary)',
                fontSize: 12,
                fontWeight: 600,
                fontFamily: 'Syne',
                cursor: running ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                opacity: running ? 0.5 : 1,
              }}>
                {a.icon}{a.label}
              </button>
            ))}
          </div>
        </div>

        {/* Difficulty */}
        <div>
          <div style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8 }}>Difficulty</div>
          <div style={{ display: 'flex', gap: 6 }}>
            {DIFFICULTIES.map(d => (
              <button key={d.id} onClick={() => setDifficulty(d.id)} disabled={running} style={{
                padding: '6px 14px',
                borderRadius: 6,
                border: `1px solid ${difficulty === d.id ? d.color : 'var(--border)'}`,
                background: difficulty === d.id ? `${d.color}18` : 'transparent',
                color: difficulty === d.id ? d.color : 'var(--text-secondary)',
                fontSize: 12, fontWeight: 600, fontFamily: 'Syne',
                cursor: running ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                opacity: running ? 0.5 : 1,
              }}>{d.label}</button>
            ))}
          </div>
        </div>

        {/* Seed */}
        <div>
          <div style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 8 }}>Seed</div>
          <input
            type="number"
            value={seed}
            onChange={e => setSeed(parseInt(e.target.value) || 42)}
            disabled={running}
            style={{
              width: 80, padding: '6px 10px', borderRadius: 6,
              background: 'var(--bg-deep)', border: '1px solid var(--border)',
              color: 'var(--accent-cyan)', fontFamily: 'JetBrains Mono', fontSize: 13,
              outline: 'none',
            }}
          />
        </div>

        {/* Actions */}
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 10, alignItems: 'center' }}>
          <button className="btn-outline" onClick={onReset} disabled={running || isResetting}>
            <RotateCcw size={13} style={{ animation: isResetting ? 'spin-slow 1s linear infinite' : 'none' }} />
            Reset
          </button>
          {running ? (
            <button className="btn-danger" onClick={onStop}>
              <Square size={13} />
              Stop
            </button>
          ) : (
            <button className="btn-primary" onClick={onRun} disabled={done || isResetting}>
              <Play size={13} />
              {done ? 'Episode Done' : obs ? 'Run Agent' : 'Initialize'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
