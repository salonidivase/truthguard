import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { CheckCircle, XCircle, Award } from 'lucide-react';

export default function VerdictPanel({ obs, state, done, gradeResult, rewardHistory }) {
  const lastResult = obs?.last_action_result || '';
  const isUnsafe = lastResult.includes('UNSAFE') || (obs?.risk_estimate || 0) >= 0.5;
  const isCorrect = lastResult.includes('✅');

  const gradeData = gradeResult ? [
    { name: 'F1', value: gradeResult.issue_f1, color: 'var(--accent-cyan)' },
    { name: 'Calibration', value: gradeResult.risk_calibration, color: 'var(--accent-purple)' },
    { name: 'Accuracy', value: gradeResult.verdict_accuracy, color: 'var(--accent-green)' },
    { name: 'Final', value: gradeResult.final_score, color: 'var(--accent-amber)' },
  ] : [];

  return (
    <div className="card" style={{ padding: 20 }}>
      <div style={{ display: 'grid', gridTemplateColumns: done && gradeResult ? '1fr 1fr 1fr' : '1fr', gap: 20 }}>
        {/* Verdict */}
        <div>
          <div style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>Final Verdict</div>
          {done ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              {isCorrect ? <CheckCircle size={32} color="var(--accent-green)" /> : <XCircle size={32} color="var(--accent-red)" />}
              <div>
                <div style={{ fontSize: 22, fontWeight: 800, fontFamily: 'Syne', color: isUnsafe ? 'var(--accent-red)' : 'var(--accent-green)' }}>
                  {isUnsafe ? '⚠ UNSAFE' : '✓ SAFE'}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>{lastResult}</div>
              </div>
            </div>
          ) : (
            <div style={{ color: 'var(--text-dim)', fontSize: 13 }}>
              {obs ? 'Agent running…' : 'Reset to start'}
            </div>
          )}
        </div>

        {/* Grade chart */}
        {done && gradeResult && (
          <div>
            <div style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>Grade Breakdown</div>
            <ResponsiveContainer width="100%" height={80}>
              <BarChart data={gradeData} barSize={18}>
                <XAxis dataKey="name" tick={{ fill: '#3d5a7a', fontSize: 9, fontFamily: 'JetBrains Mono' }} />
                <YAxis domain={[0, 1]} tick={{ fill: '#3d5a7a', fontSize: 9 }} />
                <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 6, fontFamily: 'JetBrains Mono', fontSize: 10 }} />
                <Bar dataKey="value" radius={[3, 3, 0, 0]}>
                  {gradeData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Final score */}
        {done && gradeResult && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <Award size={24} color="var(--accent-amber)" style={{ marginBottom: 8 }} />
            <div style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'JetBrains Mono', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 4 }}>Final Score</div>
            <div style={{ fontSize: 40, fontWeight: 800, fontFamily: 'JetBrains Mono', color: 'var(--accent-amber)' }}>
              {(gradeResult.final_score * 100).toFixed(0)}<span style={{ fontSize: 18 }}>%</span>
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
              F1: {gradeResult.issue_f1.toFixed(2)} · Cal: {gradeResult.risk_calibration.toFixed(2)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
