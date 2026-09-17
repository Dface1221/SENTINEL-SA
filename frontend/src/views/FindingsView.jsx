import React, { useEffect, useState } from 'react';
import { Search, Filter, ArrowUpRight, ShieldAlert, CheckCircle, Clock } from 'lucide-react';
import { fetchFindings, fetchCSEs } from '../api';

export default function FindingsView({ onSelectFinding }) {
  const [findings, setFindings] = useState([]);
  const [cses, setCses] = useState([]);
  const [search, setSearch] = useState('');
  const [cseFilter, setCseFilter] = useState('All');
  const [severityFilter, setSeverityFilter] = useState('All');
  const [typeFilter, setTypeFilter] = useState('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [fData, cData] = await Promise.all([
        fetchFindings(),
        fetchCSEs()
      ]);
      setFindings(fData);
      setCses(cData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = findings.filter(f => {
    const matchSearch = f.title.toLowerCase().includes(search.toLowerCase()) ||
                        f.description.toLowerCase().includes(search.toLowerCase()) ||
                        f.finding_id.toLowerCase().includes(search.toLowerCase());
    const matchCSE = cseFilter === 'All' || f.cse_id === cseFilter;
    const matchSev = severityFilter === 'All' || f.severity === severityFilter;
    const matchType = typeFilter === 'All' || f.finding_type === typeFilter;
    return matchSearch && matchCSE && matchSev && matchType;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Filter Controls Bar */}
      <div className="card" style={{ padding: '14px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1, minWidth: '240px' }}>
          <Search size={16} color="#64748b" />
          <input
            type="text"
            placeholder="Search findings, keywords or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#f8fafc',
              fontSize: '0.88rem',
              outline: 'none',
              width: '100%'
            }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Entity:</span>
            <select
              value={cseFilter}
              onChange={(e) => setCseFilter(e.target.value)}
              style={{ background: '#090d16', border: '1px solid var(--border-subtle)', color: '#f8fafc', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem' }}
            >
              <option value="All">All CSEs</option>
              {cses.map(c => <option key={c.cse_id} value={c.cse_id}>{c.cse_id}</option>)}
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Severity:</span>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              style={{ background: '#090d16', border: '1px solid var(--border-subtle)', color: '#f8fafc', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem' }}
            >
              <option value="All">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Type:</span>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              style={{ background: '#090d16', border: '1px solid var(--border-subtle)', color: '#f8fafc', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem' }}
            >
              <option value="All">All Types</option>
              <option value="Execution Gap">Execution Gap</option>
              <option value="Negative Space">Negative Space</option>
              <option value="Metric Gaming">Metric Gaming</option>
              <option value="Multivariate Anomaly">Multivariate Anomaly</option>
            </select>
          </div>
        </div>
      </div>

      {/* Findings Table */}
      <div className="card">
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Finding ID</th>
                <th>Entity</th>
                <th>Dimension</th>
                <th>Severity</th>
                <th>Supervisory Finding Title</th>
                <th>Confidence</th>
                <th>Review Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((f) => {
                let badgeClass = 'badge-critical';
                if (f.severity === 'High') badgeClass = 'badge-high';
                if (f.severity === 'Medium') badgeClass = 'badge-medium';

                let statusBadge = 'badge-low';
                if (f.review_status === 'Confirmed') statusBadge = 'badge-green';
                if (f.review_status === 'Dismissed') statusBadge = 'badge-secondary';
                if (f.review_status === 'Requires CSE Clarification') statusBadge = 'badge-amber';

                return (
                  <tr
                    key={f.finding_id}
                    style={{ cursor: 'pointer' }}
                    onClick={() => onSelectFinding(f.finding_id)}
                  >
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: '700', color: '#38bdf8' }}>
                      {f.finding_id}
                    </td>
                    <td style={{ fontWeight: '700' }}>
                      {f.cse_id}
                    </td>
                    <td>
                      <span className="badge badge-low">{f.finding_type}</span>
                    </td>
                    <td>
                      <span className={`badge ${badgeClass}`}>{f.severity}</span>
                    </td>
                    <td style={{ fontWeight: '600', maxWidth: '380px' }}>
                      {f.title}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: '700', color: '#34d399' }}>
                      {Math.round(f.confidence * 100)}%
                    </td>
                    <td>
                      <span className={`badge ${statusBadge}`}>{f.review_status}</span>
                    </td>
                    <td>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectFinding(f.finding_id);
                        }}
                        className="btn btn-secondary"
                        style={{ padding: '3px 8px', fontSize: '0.75rem' }}
                      >
                        Evidence
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
