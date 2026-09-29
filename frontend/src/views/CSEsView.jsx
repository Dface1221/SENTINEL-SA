import React, { useEffect, useState } from 'react';
import { Building2, Search, Filter, ArrowUpRight } from 'lucide-react';
import { fetchCSEs } from '../api';

export default function CSEsView({ onSelectCSE, onNavigate }) {
  const [cses, setCses] = useState([]);
  const [search, setSearch] = useState('');
  const [sectorFilter, setSectorFilter] = useState('All');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCSEs();
  }, []);

  const loadCSEs = async () => {
    try {
      setLoading(true);
      const res = await fetchCSEs();
      setCses(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const sectors = ['All', ...new Set(cses.map(c => c.sector))];

  const filtered = cses.filter(c => {
    const matchSearch = c.cse_id.toLowerCase().includes(search.toLowerCase()) ||
                        c.cse_name.toLowerCase().includes(search.toLowerCase());
    const matchSector = sectorFilter === 'All' || c.sector === sectorFilter;
    return matchSearch && matchSector;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Filter Controls Bar */}
      <div className="card" style={{ padding: '14px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1, minWidth: '260px' }}>
          <Search size={16} color="#64748b" />
          <input
            type="text"
            placeholder="Search CSE ID, Name or Sector..."
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

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={15} color="#64748b" />
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Sector:</span>
          <select
            value={sectorFilter}
            onChange={(e) => setSectorFilter(e.target.value)}
            style={{
              background: '#090d16',
              border: '1px solid var(--border-subtle)',
              color: '#f8fafc',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '0.82rem',
              outline: 'none'
            }}
          >
            {sectors.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

      {/* CSEs Table */}
      <div className="card">
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Entity ID</th>
                <th>Critical Sector Entity Name</th>
                <th>Sector</th>
                <th>Tier Criticality</th>
                <th>Attention Score</th>
                <th>Supervisory Review Status</th>
                <th>Detected Signals</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c) => {
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
                  <tr
                    key={c.cse_id}
                    style={{ cursor: 'pointer' }}
                    onClick={() => { onSelectCSE(c.cse_id); onNavigate('cse-profile'); }}
                  >
                    <td style={{ fontWeight: '700', color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
                      {c.cse_id}
                    </td>
                    <td style={{ fontWeight: '600' }}>
                      {c.cse_name}
                    </td>
                    <td>{c.sector}</td>
                    <td><span className="badge badge-low">{c.criticality}</span></td>
                    <td>
                      <span style={{ fontWeight: '800', fontSize: '1.1rem', color: scoreColor, fontFamily: 'var(--font-mono)' }}>
                        {c.attention_score}
                      </span>
                      <span style={{ fontSize: '0.72rem', color: '#64748b' }}> / 100</span>
                    </td>
                    <td>
                      <span className={`badge ${badgeClass}`}>{c.review_status}</span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: '#cbd5e1' }}>
                      {c.findings_count} signals
                    </td>
                    <td>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectCSE(c.cse_id);
                          onNavigate('cse-profile');
                        }}
                        className="btn btn-secondary"
                        style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                      >
                        <span>Profile</span>
                        <ArrowUpRight size={13} />
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
