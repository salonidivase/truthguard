import React, { useRef, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { Terminal, TrendingUp } from 'lucide-react';

export default function ActionLog({ log, running, rewardHistory }) {
  const logRef = useRef();
  useEffect(() => { if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight; }, [log]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12, minHeight: 0 }}>
      {/* Reward chart */}
      <div className="card" style={{ padding: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <TrendingUp size={13} color="var(--accent-cyan)" />
          <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', fontFamily: 'JetBrains Mono', color: 'var(--text-secondary)' }}>Reward History</span>
          {running && <span style={{ marginLeft: 'auto' }} className="badge badge-green animate-pulse-glow">LIVE</span>}
        </div>
        <ResponsiveContainer width="100%" height={120}>
          <LineChart data={rewardHistory.length > 0 ? rewardHistory : [{ step: 0, cumulative: 0 }]}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="step" tick={{ fill: '#3d5a7a', fontSize: 10, fontFamily: 'JetBrains Mono' }} />
            <YAxis tick={{ fill: '#3d5a7a', fontSize: 10, fontFamily: 'JetBrains Mono' }} />
            <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontFamily: 'JetBrains Mono', fontSize: 11 }} />
            <Line type="monotone" dataKey="cumulative" stroke="var(--accent-cyan)" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="reward" stroke="var(--accent-green)" strokeWidth={1} dot={false} strokeDasharray="4 2" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Action log terminal */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 8 }}>
          <Terminal size={13} color="var(--accent-cyan)" />
          <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', fontFamily: 'JetBrains Mono', color: 'var(--text-secondary)' }}>Action Log</span>
          <span style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono' }}>{log.length} events</span>
        </div>
        <div ref={logRef} style={{ flex: 1, overflowY: 'auto', padding: 12, display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 380 }}>
          {log.map((entry, i) => (
            <div key={i} className="animate-slide-left" style={{ animationDelay: '0ms', display: 'grid', gridTemplateColumns: '28px 1fr auto', gap: 10, padding: '8px 10px', borderRadius: 6, background: i === log.length - 1 && running ? 'rgba(0,229,255,0.06)' : 'var(--bg-deep)', border: `1px solid ${i === log.length - 1 && running ? 'rgba(0,229,255,0.2)' : 'var(--border)'}`, fontSize: 11, alignItems: 'start' }}>
              <div style={{ fontFamily: 'JetBrains Mono', color: 'var(--text-dim)', paddingTop: 1 }}>#{entry.step}</div>
              <div>
                <div style={{ fontFamily: 'JetBrains Mono', color: 'var(--accent-cyan)', fontSize: 10, marginBottom: 2, wordBreak: 'break-all' }}>{entry.action}</div>
                <div style={{ color: 'var(--text-secondary)', lineHeight: 1.4 }}>{entry.result}</div>
              </div>
              <div style={{ fontFamily: 'JetBrains Mono', color: entry.reward > 0 ? 'var(--accent-green)' : entry.reward < 0 ? 'var(--accent-red)' : 'var(--text-dim)', fontWeight: 700, whiteSpace: 'nowrap', paddingTop: 1 }}>
                {entry.reward > 0 ? '+' : ''}{entry.reward?.toFixed ? entry.reward.toFixed(3) : '—'}
              </div>
            </div>
          ))}
          {log.length === 0 && <div style={{ color: 'var(--text-dim)', fontSize: 12, textAlign: 'center', padding: 20 }}>No actions yet</div>}
          {running && <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--accent-cyan)', fontSize: 11, fontFamily: 'JetBrains Mono', padding: '6px 10px' }}>
            <span className="animate-blink">▊</span> Agent thinking…
          </div>}
        </div>
      </div>
    </div>
  );
}
