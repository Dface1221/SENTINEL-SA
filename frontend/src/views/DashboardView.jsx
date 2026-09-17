import React, { useEffect, useState } from 'react';
import {
  Building,
  BellRing,
  FolderArchive,
  AlertOctagon,
  EyeOff,
  Flame,
  CheckSquare,
  ArrowRight,
  TrendingDown,
  ShieldCheck,
  AlertTriangle
} from 'lucide-react';
import { fetchDashboard } from '../api';

export default function DashboardView({ onNavigate, onSelectCSE }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const res = await fetchDashboard();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
        Loading supervisory intelligence dashboard...
      </div>
    );
  }

  const stats = data?.stats || {};
  const topEntities = data?.top_entities || [];
  const findingsByCat = data?.findings_by_category || [];
  const severities = data?.severity_breakdown || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* SIH Star Demo Showcase Banner */}
      <div style={{
        background: 'linear-gradient(90deg, rgba(244, 63, 94, 0.12) 0%, rgba(245, 158, 11, 0.08) 50%, rgba(15, 23, 42, 0.6) 100%)',
        border: '1px solid rgba(244, 63, 94, 0.35)',
        borderRadius: '8px',
        padding: '16px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ background: 'rgba(244, 63, 94, 0.2)', padding: '10px', borderRadius: '8px', border: '1px solid #f43f5e' }}>
            <Flame size={24} color="#f43f5e" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="badge badge-critical" style={{ fontSize: '0.72rem' }}>HIGH PRIORITY MANUAL REVIEW</span>
              <span style={{ fontSize: '0.92rem', fontWeight: '700', color: '#f8fafc' }}>
                Star Demo Case: Northern Regional Load Despatch (CSE-07)
              </span>
            </div>
            <div style={{ fontSize: '0.82rem', color: '#cbd5e1', marginTop: '4px' }}>
              Supervisory Attention Score: <strong style={{ color: '#fb7185' }}>79 / 100</strong>. Detected fast critical closures (-85.5% vs peer), 14 unescalated critical alerts, and 3 SCADA telemetry blind spots.
            </div>
          </div>
        </div>

        <button
          onClick={() => {
            onSelectCSE('CSE-07');
            onNavigate('cse-profile');
          }}
          className="btn btn-danger"
          style={{ whiteSpace: 'nowrap' }}
        >
          <span>Inspect CSE-07 Story</span>
          <ArrowRight size={16} />
        </button>
      </div>

      {/* Top KPI Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">CSEs Analyzed</span>
            <Building size={18} color="#38bdf8" />
          </div>
          <div className="kpi-value">{stats.cses_analyzed || 0}</div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            Across 6 Critical Infrastructure Sectors
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Alerts Triaged</span>
            <BellRing size={18} color="#06b6d4" />
          </div>
          <div className="kpi-value" style={{ color: '#06b6d4' }}>
            {(stats.alerts_analyzed || 0).toLocaleString()}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            3-Month Continuous Submissions
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Cases Investigated</span>
            <FolderArchive size={18} color="#3b82f6" />
          </div>
          <div className="kpi-value">
            {(stats.cases_analyzed || 0).toLocaleString()}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            Escalated Security Incidents
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Supervisory Signals</span>
            <AlertOctagon size={18} color="#f59e0b" />
          </div>
          <div className="kpi-value" style={{ color: '#f59e0b' }}>
            {stats.supervisory_signals || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            Gaps, Anomalies & Blind Spots
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">High Priority Findings</span>
            <Flame size={18} color="#f43f5e" />
          </div>
          <div className="kpi-value" style={{ color: '#f43f5e' }}>
            {stats.high_priority_findings || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            Critical Operational Concerns
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Potential Blind Spots</span>
            <EyeOff size={18} color="#c084fc" />
          </div>
          <div className="kpi-value" style={{ color: '#c084fc' }}>
            {stats.potential_blind_spots || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            Negative Space Telemetry Voids
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Entities Requiring Review</span>
            <AlertTriangle size={18} color="#fb923c" />
          </div>
          <div className="kpi-value" style={{ color: '#fb923c' }}>
            {stats.entities_requiring_review || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            {'Attention Score >= 50'}
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Active Remediations</span>
            <CheckSquare size={18} color="#10b981" />
          </div>
          <div className="kpi-value" style={{ color: '#10b981' }}>
            {stats.open_remediation_actions || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            "How to Heal" Corrective Actions
          </div>
        </div>
      </div>

      {/* Middle Grid: Category Breakdown & Severity Distribution */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Finding Categories */}
        <div className="card">
          <div className="card-title">
            <span>Findings by Supervisory Dimension</span>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>FIND → PROVE → PRIORITIZE</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '10px' }}>
            {findingsByCat.map((item) => {
              const maxCount = Math.max(...findingsByCat.map(x => x.count), 1);
              const pct = (item.count / maxCount) * 100;
              let barColor = '#3b82f6';
              if (item.category === 'Execution Gap') barColor = '#f43f5e';
              if (item.category === 'Negative Space') barColor = '#c084fc';
              if (item.category === 'Metric Gaming') barColor = '#f59e0b';
              if (item.category === 'Multivariate Anomaly') barColor = '#06b6d4';

              return (
                <div key={item.category}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                    <span style={{ fontWeight: '600', color: '#f1f5f9' }}>{item.category}</span>
                    <span style={{ color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>{item.count} findings</span>
                  </div>
                  <div className="progress-bar-bg">
                    <div
                      className="progress-bar-fill"
                      style={{ width: `${pct}%`, background: barColor }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Severity Distribution */}
        <div className="card">
          <div className="card-title">
            <span>Severity & Attention Intensity</span>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Supervisory Weight</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '10px' }}>
            {severities.map((item) => {
              const totalFindings = severities.reduce((a, b) => a + b.count, 0) || 1;
              const pct = Math.round((item.count / totalFindings) * 100);

              return (
                <div key={item.severity}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '4px' }}>
                    <span style={{ fontWeight: '600', color: item.color }}>{item.severity}</span>
                    <span style={{ color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>{item.count} ({pct}%)</span>
                  </div>
                  <div className="progress-bar-bg">
                    <div
                      className="progress-bar-fill"
                      style={{ width: `${pct}%`, background: item.color }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Priority Entities Ranking Table */}
      <div className="card">
        <div className="card-title">
          <span>Priority Entities Requiring Supervisory Oversight</span>
          <button
            onClick={() => onNavigate('cses')}
            className="btn btn-secondary"
            style={{ fontSize: '0.78rem', padding: '4px 10px' }}
          >
            View All Entities
          </button>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Entity ID</th>
                <th>Entity Name</th>
                <th>Sector</th>
                <th>Criticality</th>
                <th>Attention Score</th>
                <th>Status</th>
                <th>Signals</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {topEntities.slice(0, 7).map((c) => {
                let badgeClass = 'badge-green';
                let scoreColor = '#34d399';
                if (c.attention_score >= 70) {
                  badgeClass = 'badge-critical';
                  scoreColor = '#fb7185';
                } else if (c.attention_score >= 50) {
                  badgeClass = 'badge-high';
                  scoreColor = '#fb923c';
                } else if (c.attention_score >= 30) {
                  badgeClass = 'badge-medium';
                  scoreColor = '#fcd34d';
                }

                return (
                  <tr key={c.cse_id} style={{ cursor: 'pointer' }} onClick={() => { onSelectCSE(c.cse_id); onNavigate('cse-profile'); }}>
                    <td style={{ fontWeight: '700', color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{c.cse_id}</td>
                    <td style={{ fontWeight: '600' }}>{c.name}</td>
                    <td>{c.sector}</td>
                    <td><span className="badge badge-low">{c.criticality}</span></td>
                    <td>
                      <span style={{ fontWeight: '800', fontSize: '1.05rem', color: scoreColor, fontFamily: 'var(--font-mono)' }}>
                        {c.attention_score}
                      </span>
                      <span style={{ fontSize: '0.72rem', color: '#64748b' }}> / 100</span>
                    </td>
                    <td>
                      <span className={`badge ${badgeClass}`}>{c.status}</span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: '#cbd5e1' }}>{c.findings_count} findings</td>
                    <td>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectCSE(c.cse_id);
                          onNavigate('cse-profile');
                        }}
                        className="btn btn-secondary"
                        style={{ padding: '3px 10px', fontSize: '0.75rem' }}
                      >
                        Inspect
                      </button>
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
