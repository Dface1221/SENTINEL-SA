import React, { useEffect, useState } from 'react';
import { HeartHandshake, PlusCircle, CheckCircle, Clock, Filter, AlertTriangle } from 'lucide-react';
import { fetchRemediations, createRemediation, updateRemediation, fetchCSEs } from '../api';

export default function RemediationView() {
  const [actions, setActions] = useState([]);
  const [cses, setCses] = useState([]);
  const [statusFilter, setStatusFilter] = useState('All');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newAction, setNewAction] = useState({
    cse_id: '',
    title: '',
    owner: 'CSE SOC Operations Lead',
    due_date: '2026-10-31',
    priority: 'High',
    verification_metric: '',
    notes: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [actData, cData] = await Promise.all([
        fetchRemediations(),
        fetchCSEs()
      ]);
      setActions(actData);
      setCses(cData);
      if (cData.length > 0 && !newAction.cse_id) {
        setNewAction(prev => ({ ...prev, cse_id: cData[0].cse_id }));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (actionId, newStatus) => {
    try {
      await updateRemediation(actionId, { status: newStatus });
      setActions(prev => prev.map(a => a.action_id === actionId ? { ...a, status: newStatus } : a));
    } catch (err) {
      alert(`Update failed: ${err.message}`);
    }
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    if (!newAction.title || !newAction.verification_metric) {
      alert('Please fill in the action title and verification metric.');
      return;
    }
    try {
      await createRemediation(newAction);
      setShowModal(false);
      setNewAction({
        cse_id: cses[0]?.cse_id || '',
        title: '',
        owner: 'CSE SOC Operations Lead',
        due_date: '2026-10-31',
        priority: 'High',
        verification_metric: '',
        notes: ''
      });
      loadData();
    } catch (err) {
      alert(`Creation failed: ${err.message}`);
    }
  };

  const filtered = actions.filter(a => statusFilter === 'All' || a.status === statusFilter);

  const statusCounts = {
    total: actions.length,
    open: actions.filter(a => a.status === 'Open').length,
    inProgress: actions.filter(a => a.status === 'In Progress').length,
    completed: actions.filter(a => a.status === 'Completed').length,
    verification: actions.filter(a => a.status === 'Verification Pending').length
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* KPI Status Strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        <div className="card">
          <div className="kpi-label">Total Corrective Actions</div>
          <div className="kpi-value" style={{ color: '#38bdf8' }}>{statusCounts.total}</div>
        </div>
        <div className="card">
          <div className="kpi-label">Open Actions</div>
          <div className="kpi-value" style={{ color: '#fb923c' }}>{statusCounts.open}</div>
        </div>
        <div className="card">
          <div className="kpi-label">In Progress</div>
          <div className="kpi-value" style={{ color: '#f59e0b' }}>{statusCounts.inProgress}</div>
        </div>
        <div className="card">
          <div className="kpi-label">Completed / Verified</div>
          <div className="kpi-value" style={{ color: '#10b981' }}>{statusCounts.completed + statusCounts.verification}</div>
        </div>
      </div>

      {/* Control Bar */}
      <div className="card" style={{ padding: '14px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Filter size={15} color="#64748b" />
          <span style={{ fontSize: '0.82rem', color: '#94a3b8' }}>Filter Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              background: '#090d16',
              border: '1px solid var(--border-subtle)',
              color: '#f8fafc',
              padding: '4px 10px',
              borderRadius: '6px',
              fontSize: '0.82rem'
            }}
          >
            <option value="All">All Statuses ({actions.length})</option>
            <option value="Open">Open ({statusCounts.open})</option>
            <option value="In Progress">In Progress ({statusCounts.inProgress})</option>
            <option value="Verification Pending">Verification Pending</option>
            <option value="Completed">Completed</option>
          </select>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="btn btn-primary"
          style={{ fontSize: '0.82rem' }}
        >
          <PlusCircle size={15} />
          <span>Create Remediation Action</span>
        </button>
      </div>

      {/* Remediations Table */}
      <div className="card">
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Action ID</th>
                <th>Entity</th>
                <th>Priority</th>
                <th>Corrective Action Item</th>
                <th>Designated Owner</th>
                <th>Target Due Date</th>
                <th>Quantitative Verification Metric</th>
                <th>Progress Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((act) => {
                let pBadge = 'badge-critical';
                if (act.priority === 'High') pBadge = 'badge-high';
                if (act.priority === 'Medium') pBadge = 'badge-amber';

                return (
                  <tr key={act.action_id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: '700', color: '#38bdf8' }}>
                      {act.action_id}
                    </td>
                    <td style={{ fontWeight: '700' }}>
                      {act.cse_id}
                    </td>
                    <td>
                      <span className={`badge ${pBadge}`}>{act.priority}</span>
                    </td>
                    <td style={{ fontWeight: '600', maxWidth: '300px' }}>
                      {act.title}
                    </td>
                    <td style={{ fontSize: '0.82rem', color: '#cbd5e1' }}>
                      {act.owner}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>
                      {act.due_date || 'N/A'}
                    </td>
                    <td style={{ fontSize: '0.82rem', color: '#34d399', maxWidth: '260px' }}>
                      {act.verification_metric}
                    </td>
                    <td>
                      <select
                        value={act.status}
                        onChange={(e) => handleStatusUpdate(act.action_id, e.target.value)}
                        style={{
                          background: '#090d16',
                          border: '1px solid var(--border-subtle)',
                          color: act.status === 'Completed' ? '#34d399' : (act.status === 'In Progress' ? '#f59e0b' : '#f8fafc'),
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '0.78rem',
                          fontWeight: '600'
                        }}
                      >
                        <option value="Open">Open</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Verification Pending">Verification Pending</option>
                        <option value="Completed">Completed</option>
                        <option value="Closed">Closed</option>
                      </select>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Remediation Modal Form */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#f8fafc' }}>
                Create Supervisory Corrective Action
              </h3>
            </div>
            <form onSubmit={handleCreateSubmit}>
              <div className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Target Entity:</label>
                  <select
                    value={newAction.cse_id}
                    onChange={(e) => setNewAction({ ...newAction, cse_id: e.target.value })}
                    style={{ width: '100%', padding: '8px', background: '#090d16', border: '1px solid var(--border-subtle)', color: '#fff', borderRadius: '4px' }}
                  >
                    {cses.map(c => <option key={c.cse_id} value={c.cse_id}>{c.cse_id} - {c.cse_name}</option>)}
                  </select>
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Action Title:</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Implement mandatory forensic artifact attachment checklist"
                    value={newAction.title}
                    onChange={(e) => setNewAction({ ...newAction, title: e.target.value })}
                    style={{ width: '100%', padding: '8px', background: '#090d16', border: '1px solid var(--border-subtle)', color: '#fff', borderRadius: '4px' }}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Designated Owner:</label>
                  <input
                    type="text"
                    value={newAction.owner}
                    onChange={(e) => setNewAction({ ...newAction, owner: e.target.value })}
                    style={{ width: '100%', padding: '8px', background: '#090d16', border: '1px solid var(--border-subtle)', color: '#fff', borderRadius: '4px' }}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Quantitative Verification Metric:</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Critical-alert median investigation duration >= 40 minutes"
                    value={newAction.verification_metric}
                    onChange={(e) => setNewAction({ ...newAction, verification_metric: e.target.value })}
                    style={{ width: '100%', padding: '8px', background: '#090d16', border: '1px solid var(--border-subtle)', color: '#fff', borderRadius: '4px' }}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div>
                    <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Priority:</label>
                    <select
                      value={newAction.priority}
                      onChange={(e) => setNewAction({ ...newAction, priority: e.target.value })}
                      style={{ width: '100%', padding: '8px', background: '#090d16', border: '1px solid var(--border-subtle)', color: '#fff', borderRadius: '4px' }}
                    >
                      <option value="Critical">Critical</option>
                      <option value="High">High</option>
                      <option value="Medium">Medium</option>
                      <option value="Low">Low</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'block', marginBottom: '4px' }}>Target Due Date:</label>
                    <input
                      type="date"
                      value={newAction.due_date}
                      onChange={(e) => setNewAction({ ...newAction, due_date: e.target.value })}
                      style={{ width: '100%', padding: '8px', background: '#090d16', border: '1px solid var(--border-subtle)', color: '#fff', borderRadius: '4px' }}
                    />
                  </div>
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Action
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
