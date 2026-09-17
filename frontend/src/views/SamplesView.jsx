import React, { useEffect, useState } from 'react';
import { Crosshair, Check, AlertCircle, ChevronDown, ChevronUp, Shield } from 'lucide-react';
import { fetchSamples } from '../api';

export default function SamplesView({ onSelectFinding }) {
  const [samples, setSamples] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSamples();
  }, []);

  const loadSamples = async () => {
    try {
      setLoading(true);
      const res = await fetchSamples();
      setSamples(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>Prioritizing representative alert samples...</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Intro Banner */}
      <div className="card" style={{ padding: '16px 20px', borderLeft: '4px solid #06b6d4' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Crosshair size={18} color="#06b6d4" />
          <span>Intelligent Alert Sample Prioritization ({samples.length} Representative Alerts)</span>
        </h3>
        <p style={{ fontSize: '0.84rem', color: '#cbd5e1', marginTop: '4px', lineHeight: 1.5 }}>
          Instead of requiring supervisors to inspect tens of thousands of alert records, SAT-SA’s sampling engine extracts high-consequence representative alerts displaying significant multi-signal anomalies. Each sample contains transparent justification checkmarks.
        </p>
      </div>

      {/* Samples Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {samples.map((s) => {
          const isExpanded = expandedId === s.alert_id;
          const isCritical = s.priority === 'Critical';

          return (
            <div
              key={s.alert_id}
              className="card"
              style={{
                borderColor: isCritical ? 'rgba(244, 63, 94, 0.4)' : 'var(--border-subtle)',
                background: isCritical ? 'linear-gradient(135deg, rgba(244, 63, 94, 0.05) 0%, var(--bg-card) 100%)' : 'var(--bg-card)'
              }}
            >
              {/* Header row */}
              <div
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
                onClick={() => setExpandedId(isExpanded ? null : s.alert_id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span className={`badge ${isCritical ? 'badge-critical' : 'badge-high'}`}>
                    {s.priority} PRIORITY
                  </span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: '800', fontSize: '1.05rem', color: '#38bdf8' }}>
                    {s.alert_id}
                  </span>
                  <span style={{ fontWeight: '700', color: '#f8fafc' }}>
                    [{s.cse_id}] {s.category}
                  </span>
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                    on {s.asset_name}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  <div style={{ fontSize: '0.8rem', color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>
                    {s.timestamp}
                  </div>
                  {isExpanded ? <ChevronUp size={18} color="#94a3b8" /> : <ChevronDown size={18} color="#94a3b8" />}
                </div>
              </div>

              {/* Justification Checkmarks ("Why this alert was selected") */}
              <div style={{ marginTop: '14px', background: 'rgba(9, 13, 22, 0.7)', padding: '12px 16px', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: '700', textTransform: 'uppercase', color: '#06b6d4', marginBottom: '8px', letterSpacing: '0.04em' }}>
                  Why this alert was selected for supervisory review:
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '8px' }}>
                  {s.selection_reasons.map((r, idx) => (
                    <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#cbd5e1' }}>
                      <div style={{ color: '#10b981', display: 'flex', alignItems: 'center' }}>
                        <Check size={15} strokeWidth={3} />
                      </div>
                      <span>{r}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Expanded investigation detail drawer */}
              {isExpanded && (
                <div style={{ marginTop: '14px', paddingTop: '14px', borderTop: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', fontSize: '0.82rem' }}>
                    <div>
                      <span style={{ color: '#64748b' }}>Detection Source:</span>
                      <div style={{ fontWeight: '600', color: '#f8fafc' }}>{s.source}</div>
                    </div>
                    <div>
                      <span style={{ color: '#64748b' }}>Closure Duration:</span>
                      <div style={{ fontWeight: '600', color: s.duration_minutes < 15 ? '#fb7185' : '#38bdf8' }}>
                        {s.duration_minutes} minutes
                      </div>
                    </div>
                    <div>
                      <span style={{ color: '#64748b' }}>Associated Case:</span>
                      <div style={{ fontWeight: '600', color: '#f8fafc' }}>{s.case_id}</div>
                    </div>
                    <div>
                      <span style={{ color: '#64748b' }}>Escalated to IR:</span>
                      <div style={{ fontWeight: '600', color: s.escalated ? '#34d399' : '#fb7185' }}>
                        {s.escalated ? 'Yes (Documented)' : 'No (Unescalated Gap)'}
                      </div>
                    </div>
                  </div>

                  <div>
                    <span style={{ fontSize: '0.78rem', color: '#64748b' }}>Raw Investigation Note:</span>
                    <div style={{ background: '#090d16', padding: '8px 12px', borderRadius: '4px', fontSize: '0.82rem', color: '#94a3b8', marginTop: '4px', border: '1px solid var(--border-subtle)', fontStyle: 'italic' }}>
                      "{s.investigation_notes}"
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
