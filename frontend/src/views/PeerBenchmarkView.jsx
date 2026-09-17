import React, { useEffect, useState } from 'react';
import { BarChart3, TrendingDown, ArrowUpDown } from 'lucide-react';
import { fetchBenchmarks } from '../api';

export default function PeerBenchmarkView({ onSelectCSE, onNavigate }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBenchmarks();
  }, []);

  const loadBenchmarks = async () => {
    try {
      setLoading(true);
      const res = await fetchBenchmarks();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>Calculating sector peer benchmarks and distributions...</div>;
  }

  const entities = Object.values(data?.entity_metrics || {});
  const medians = data?.global_medians || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Peer Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div className="card">
          <div className="kpi-label">Peer Median Critical Closure</div>
          <div className="kpi-value" style={{ color: '#38bdf8' }}>{medians.crit_median_dur} min</div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>Established Sector Baseline</div>
        </div>

        <div className="card">
          <div className="kpi-label">Peer Median Critical Escalation</div>
          <div className="kpi-value" style={{ color: '#10b981' }}>{medians.crit_esc_rate}%</div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>Tier-2/IR Escalation Norm</div>
        </div>

        <div className="card">
          <div className="kpi-label">Peer Median Telemetry Coverage</div>
          <div className="kpi-value" style={{ color: '#06b6d4' }}>{medians.telemetry_coverage}%</div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>Continuous Ingestion Health</div>
        </div>

        <div className="card">
          <div className="kpi-label">Peer Median Evidence Count</div>
          <div className="kpi-value" style={{ color: '#f59e0b' }}>{medians.avg_evidence} items</div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>Per Case Investigation</div>
        </div>
      </div>

      {/* Benchmarking Comparison Table */}
      <div className="card">
        <div className="card-title">
          <span>Entity Benchmarks vs Established Peer Medians</span>
          <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Objective Deviation Metrics</span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Entity ID</th>
                <th>Sector</th>
                <th>Critical Closure Duration</th>
                <th>Closure Deviation vs Peer</th>
                <th>Critical Escalation Rate</th>
                <th>Escalation Deviation vs Peer</th>
                <th>Telemetry Coverage</th>
                <th>Supervisory Evaluation</th>
              </tr>
            </thead>
            <tbody>
              {entities.map((m) => {
                const isFast = m.crit_median_dur < 15;
                const isLowEsc = m.crit_esc_rate < 35;
                const isGapped = isFast || isLowEsc || m.telemetry_coverage < 80;

                return (
                  <tr
                    key={m.cse_id}
                    style={{ cursor: 'pointer' }}
                    onClick={() => { onSelectCSE(m.cse_id); onNavigate('cse-profile'); }}
                  >
                    <td style={{ fontWeight: '700', color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
                      {m.cse_id}
                      {m.cse_id === 'CSE-07' && (
                        <span className="badge badge-critical" style={{ marginLeft: '6px', fontSize: '0.65rem' }}>
                          DEMO
                        </span>
                      )}
                    </td>
                    <td>{m.sector}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: '700', color: isFast ? '#fb7185' : '#f8fafc' }}>
                      {m.crit_median_dur} min
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: '700', color: m.crit_dur_deviation < -50 ? '#fb7185' : '#34d399' }}>
                      {m.crit_dur_deviation > 0 ? `+${m.crit_dur_deviation}%` : `${m.crit_dur_deviation}%`}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: '700', color: isLowEsc ? '#fb7185' : '#f8fafc' }}>
                      {m.crit_esc_rate}%
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: '700', color: m.crit_esc_deviation < -40 ? '#fb7185' : '#34d399' }}>
                      {m.crit_esc_deviation > 0 ? `+${m.crit_esc_deviation}%` : `${m.crit_esc_deviation}%`}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: '700', color: m.telemetry_coverage < 85 ? '#fb923c' : '#34d399' }}>
                      {m.telemetry_coverage}%
                    </td>
                    <td>
                      {isGapped ? (
                        <span className="badge badge-critical">Requires Review</span>
                      ) : (
                        <span className="badge badge-green">Within Peer Range</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
