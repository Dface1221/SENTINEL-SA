import React, { useEffect, useState } from 'react';
import { ListTodo, CheckCircle, Clock, AlertTriangle, HelpCircle, XCircle } from 'lucide-react';
import { fetchReviewQueue, updateFindingStatus } from '../api';

export default function ReviewQueueView({ onSelectFinding }) {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);

  const [filterPriority, setFilterPriority] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [filterCSE, setFilterCSE] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  useEffect(() => {
    loadQueue();
  }, []);

  const loadQueue = async () => {
    try {
      setLoading(true);
      const res = await fetchReviewQueue();
      setQueue(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (findingId, newStatus) => {
    try {
      setUpdatingId(findingId);
      await updateFindingStatus(findingId, newStatus);
      setQueue(prev => prev.map(item => item.finding_id === findingId ? { ...item, review_status: newStatus } : item));
    } catch (err) {
      alert(`Status update failed: ${err.message}`);
    } finally {
      setUpdatingId(null);
    }
  };

  const filteredQueue = queue.filter(item => {
    if (filterPriority && item.priority !== filterPriority) return false;
    if (filterCategory && item.category !== filterCategory) return false;
    if (filterCSE && item.cse_id !== filterCSE) return false;
    if (filterStatus && item.review_status !== filterStatus) return false;
    return true;
  });

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>Loading prioritized review queue...</div>;
  }

  // Extract unique values for filters
  const uniquePriorities = [...new Set(queue.map(item => item.priority))];
  const uniqueCategories = [...new Set(queue.map(item => item.category))];
  const uniqueCSEs = [...new Set(queue.map(item => item.cse_id))];
  const uniqueStatuses = [...new Set(queue.map(item => item.review_status))];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Overview Info Banner */}
      <div className="card" style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#f8fafc' }}>
            Active Supervisory Triage Queue ({filteredQueue.length} items)
          </h3>
          <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginTop: '2px' }}>
            Sorted by Risk Weight, Confidence, and Negative-Space Criticality. Update review status to record supervisor decisions.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '16px', fontSize: '0.82rem' }}>
          <div><strong style={{ color: '#fb7185' }}>{queue.filter(q => q.priority === 'P1').length}</strong> P1 Critical</div>
          <div><strong style={{ color: '#fb923c' }}>{queue.filter(q => q.priority === 'P2').length}</strong> P2 Elevated</div>
          <div><strong style={{ color: '#38bdf8' }}>{queue.filter(q => q.priority === 'P3').length}</strong> P3 Standard</div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ padding: '12px 20px', display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#cbd5e1' }}>Filters:</span>
        <select value={filterPriority} onChange={e => setFilterPriority(e.target.value)} style={{ background: '#090d16', border: '1px solid var(--border-subtle)', color: '#f8fafc', padding: '6px 12px', borderRadius: '4px', fontSize: '0.8rem' }}>
          <option value="">All Priorities</option>
          {uniquePriorities.map(p => <option key={p} value={p}>{p}</option>)}
        </select>
        <select value={filterCategory} onChange={e => setFilterCategory(e.target.value)} style={{ background: '#090d16', border: '1px solid var(--border-subtle)', color: '#f8fafc', padding: '6px 12px', borderRadius: '4px', fontSize: '0.8rem' }}>
          <option value="">All Categories</option>
          {uniqueCategories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={filterCSE} onChange={e => setFilterCSE(e.target.value)} style={{ background: '#090d16', border: '1px solid var(--border-subtle)', color: '#f8fafc', padding: '6px 12px', borderRadius: '4px', fontSize: '0.8rem' }}>
          <option value="">All Entities</option>
          {uniqueCSEs.map(cse => <option key={cse} value={cse}>{cse}</option>)}
        </select>
        <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} style={{ background: '#090d16', border: '1px solid var(--border-subtle)', color: '#f8fafc', padding: '6px 12px', borderRadius: '4px', fontSize: '0.8rem' }}>
          <option value="">All Statuses</option>
          {uniqueStatuses.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {/* Queue Table */}
      <div className="card">
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Priority</th>
                <th>Entity</th>
                <th>Category</th>
                <th>Supervisory Finding</th>
                <th>Attention Weight</th>
                <th>Evidence Items</th>
                <th>Recommended Primary Action</th>
                <th>Review Status Decision</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredQueue.map((item) => {
                const isP1 = item.priority === 'P1';
                const isP2 = item.priority === 'P2';
                const pColor = isP1 ? '#f43f5e' : (isP2 ? '#f97316' : '#0284c7');

                return (
                  <tr key={item.finding_id}>
                    <td>
                      <span style={{
                        background: `${pColor}22`,
                        color: pColor,
                        border: `1px solid ${pColor}55`,
                        padding: '3px 8px',
                        borderRadius: '4px',
                        fontWeight: '800',
                        fontSize: '0.78rem',
                        fontFamily: 'var(--font-mono)'
                      }}>
                        {item.priority}
                      </span>
                    </td>
                    <td style={{ fontWeight: '700', color: '#f8fafc' }}>
                      {item.cse_id}
                    </td>
                    <td>
                      <span className="badge badge-low">{item.category}</span>
                    </td>
                    <td style={{ fontWeight: '600', maxWidth: '320px' }}>
                      {item.title}
                    </td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: '700', color: item.risk_score >= 80 ? '#fb7185' : '#38bdf8' }}>
                        {item.risk_score}
                      </span>
                      <span style={{ fontSize: '0.72rem', color: '#64748b' }}> / 100</span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: '#cbd5e1' }}>
                      {item.evidence_count} records
                    </td>
                    <td style={{ fontSize: '0.8rem', color: '#94a3b8', maxWidth: '280px' }}>
                      {item.primary_action}
                    </td>
                    <td>
                      <select
                        value={item.review_status}
                        disabled={updatingId === item.finding_id}
                        onChange={(e) => handleStatusChange(item.finding_id, e.target.value)}
                        style={{
                          background: '#090d16',
                          border: '1px solid var(--border-subtle)',
                          color: item.review_status === 'Confirmed' ? '#34d399' : (item.review_status === 'Dismissed' ? '#94a3b8' : '#f8fafc'),
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '0.8rem',
                          fontWeight: '600'
                        }}
                      >
                        <option value="New">New</option>
                        <option value="Under Review">Under Review</option>
                        <option value="Confirmed">Confirmed</option>
                        <option value="Dismissed">Dismissed</option>
                        <option value="Requires CSE Clarification">Requires Clarification</option>
                      </select>
                    </td>
                    <td>
                      <button
                        onClick={() => onSelectFinding(item.finding_id)}
                        className="btn btn-secondary"
                        style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                      >
                        Examine
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
