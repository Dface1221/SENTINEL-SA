import React, { useEffect, useState } from 'react';
import { Grid, EyeOff, Check, AlertTriangle, X, HelpCircle } from 'lucide-react';
import { fetchNegativeSpaceMatrix } from '../api';

export default function NegativeSpaceView({ onSelectCSE, onNavigate }) {
  const [matrix, setMatrix] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMatrix();
  }, []);

  const loadMatrix = async () => {
    try {
      setLoading(true);
      const res = await fetchNegativeSpaceMatrix();
      setMatrix(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>Loading negative space heatmap matrix...</div>;
  }

  const columns = [
    { key: 'critical_asset_telemetry', label: 'Critical Asset Telemetry' },
    { key: 'alert_categories', label: 'Alert Category Spectrum' },
    { key: 'investigation_depth', label: 'Investigation Evidence Depth' },
    { key: 'escalation_rigor', label: 'Escalation Rigor & SLAs' },
    { key: 'root_cause_remediation', label: 'Root-Cause Remediation' },
    { key: 'monitoring_activity', label: 'Expected Baseline Activity' },
    { key: 'operational_integrity', label: 'Operational Metric Integrity' }
  ];

  const renderCell = (state) => {
    let className = 'heatmap-cell cell-present';
    let label = 'Evidence Present';
    let icon = <Check size={13} />;

    if (state === 'Missing') {
      className = 'heatmap-cell cell-missing';
      label = 'Missing / Blind Spot';
      icon = <X size={13} />;
    } else if (state === 'Partial') {
      className = 'heatmap-cell cell-partial';
      label = 'Partial Evidence';
      icon = <AlertTriangle size={13} />;
    } else if (state === 'Requires Validation') {
      className = 'heatmap-cell cell-validate';
      label = 'Requires Validation';
      icon = <HelpCircle size={13} />;
    }

    return (
      <div className={className} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
        {icon}
        <span>{label}</span>
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Intro Header & Legend */}
      <div className="card" style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <EyeOff size={18} color="#c084fc" />
            <span>Negative Space Operational Heatmap</span>
          </h3>
          <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginTop: '3px' }}>
            Analyzes what SHOULD exist but is absent (telemetry voids, omitted MITRE threat categories, missing root-cause records).
          </p>
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.78rem' }}>
          <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }} />
            Evidence Present
          </span>
          <span style={{ color: '#fcd34d', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b' }} />
            Partial Telemetry
          </span>
          <span style={{ color: '#fb7185', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f43f5e' }} />
            Missing / Blind Spot
          </span>
          <span style={{ color: '#c084fc', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#8b5cf6' }} />
            Requires Validation
          </span>
        </div>
      </div>

      {/* Heatmap Grid Table */}
      <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ margin: 0 }}>
            <thead>
              <tr>
                <th style={{ minWidth: '180px' }}>Critical Sector Entity</th>
                <th style={{ minWidth: '90px' }}>Attention Score</th>
                {columns.map(col => (
                  <th key={col.key} style={{ minWidth: '160px', textAlign: 'center' }}>
                    {col.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matrix.map((row) => (
                <tr
                  key={row.cse_id}
                  style={{ cursor: 'pointer' }}
                  onClick={() => { onSelectCSE(row.cse_id); onNavigate('cse-profile'); }}
                >
                  <td style={{ fontWeight: '700', color: '#f8fafc' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{row.cse_id}</span>
                      <span style={{ fontSize: '0.82rem', color: '#cbd5e1' }}>{row.cse_name.slice(0, 22)}...</span>
                    </div>
                  </td>
                  <td>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontWeight: '800',
                      color: row.attention_score >= 70 ? '#fb7185' : (row.attention_score >= 50 ? '#fb923c' : '#34d399')
                    }}>
                      {row.attention_score}
                    </span>
                  </td>
                  {columns.map(col => (
                    <td key={col.key} style={{ padding: '8px' }}>
                      {renderCell(row.pillars[col.key])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
