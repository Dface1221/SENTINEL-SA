import React, { useEffect, useState } from 'react';
import { CheckCheck, CheckCircle2, XCircle, AlertCircle, UserCheck } from 'lucide-react';
import { fetchValidation } from '../api';

export default function ValidationView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadValidation();
  }, []);

  const loadValidation = async () => {
    try {
      setLoading(true);
      const res = await fetchValidation();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>Evaluating empirical ground-truth validation metrics...</div>;
  }

  const overall = data?.overall || {};
  const byCategory = data?.by_category || {};
  const evaluations = data?.evaluations || [];
  const human = data?.human_validation || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Intro Banner */}
      <div className="card" style={{ padding: '16px 20px', borderLeft: '4px solid #10b981' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCheck size={20} color="#10b981" />
          <span>Empirical Analytics Validation against Ground Truth (SIH Evaluation Standard)</span>
        </h3>
        <p style={{ fontSize: '0.84rem', color: '#cbd5e1', marginTop: '4px', lineHeight: 1.5 }}>
          To demonstrate rigorous algorithmic reliability without black-box opacity, the SAT-SA supervisory engine is benchmarked against internal ground-truth controls. True Positives, False Positives, False Negatives, Precision, Recall, and F1 Score are computed dynamically from active database state.
        </p>
      </div>

      {/* KPI Cards: Precision, Recall, F1 Score */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        <div className="kpi-card">
          <div className="kpi-label">Precision Rate</div>
          <div className="kpi-value" style={{ color: '#10b981' }}>
            {Math.round(overall.precision * 100)}%
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            TP / (TP + FP) — Detection Reliability
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">Recall (Sensitivity)</div>
          <div className="kpi-value" style={{ color: '#06b6d4' }}>
            {Math.round(overall.recall * 100)}%
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            TP / (TP + FN) — Coverage Completeness
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">F1 Composite Score</div>
          <div className="kpi-value" style={{ color: '#38bdf8' }}>
            {overall.f1_score}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            Harmonic Mean of Precision & Recall
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-label">Ground Truth Controls</div>
          <div className="kpi-value" style={{ color: '#f59e0b' }}>
            {overall.total_ground_truth_items || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            {overall.true_positives} TP | {overall.true_negatives} Clean Controls
          </div>
        </div>
      </div>

      {/* Human-in-the-loop Validation Tracking */}
      <div className="card">
        <div className="card-title">
          <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <UserCheck size={18} color="#06b6d4" />
            <span>Human-in-the-Loop Supervisory Feedback Calibration</span>
          </span>
          <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Supervisory Decisions Recorded</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px', marginTop: '8px' }}>
          <div style={{ background: '#090d16', padding: '12px', borderRadius: '6px', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
            <div style={{ fontSize: '1.4rem', fontWeight: '800', color: '#34d399', fontFamily: 'var(--font-mono)' }}>{human.confirmed_by_expert}</div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' }}>Confirmed Findings</div>
          </div>
          <div style={{ background: '#090d16', padding: '12px', borderRadius: '6px', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
            <div style={{ fontSize: '1.4rem', fontWeight: '800', color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>{human.dismissed_by_expert}</div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' }}>Dismissed as Benign</div>
          </div>
          <div style={{ background: '#090d16', padding: '12px', borderRadius: '6px', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
            <div style={{ fontSize: '1.4rem', fontWeight: '800', color: '#f59e0b', fontFamily: 'var(--font-mono)' }}>{human.requires_clarification}</div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' }}>Awaiting Entity Response</div>
          </div>
          <div style={{ background: '#090d16', padding: '12px', borderRadius: '6px', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
            <div style={{ fontSize: '1.4rem', fontWeight: '800', color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>{human.total_reviewed}</div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' }}>Total Expert Triaged</div>
          </div>
        </div>
      </div>

      {/* Ground Truth Evaluation Table */}
      <div className="card">
        <div className="card-title">
          <span>Ground Truth Benchmark Verification Table</span>
          <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Dynamic Empirical Evaluation</span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Test Control ID</th>
                <th>Entity</th>
                <th>Target Operational Pattern</th>
                <th>Expected Flag</th>
                <th>Algorithm Result</th>
                <th>Empirical Status</th>
                <th>Benchmark Rationale</th>
              </tr>
            </thead>
            <tbody>
              {evaluations.map((ev) => {
                const isTP = ev.status.includes('True Positive');
                const isTN = ev.status.includes('True Negative');
                const isFP = ev.status.includes('False Positive');
                const isFN = ev.status.includes('False Negative');

                let statusBadge = 'badge-green';
                let icon = <CheckCircle2 size={13} />;
                if (isTN) {
                  statusBadge = 'badge-low';
                } else if (isFP || isFN) {
                  statusBadge = 'badge-critical';
                  icon = <XCircle size={13} />;
                }

                return (
                  <tr key={ev.ground_truth_id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: '700', color: '#38bdf8' }}>
                      {ev.ground_truth_id}
                    </td>
                    <td style={{ fontWeight: '700' }}>
                      {ev.cse_id}
                    </td>
                    <td style={{ fontWeight: '600', maxWidth: '300px' }}>
                      {ev.title}
                    </td>
                    <td>
                      <span className={`badge ${ev.expected_flag ? 'badge-amber' : 'badge-low'}`}>
                        {ev.expected_flag ? 'Expected Concern' : 'Healthy Control'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${ev.detected ? 'badge-critical' : 'badge-green'}`}>
                        {ev.detected ? 'Flagged by Engine' : 'No Concern'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${statusBadge}`} style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                        {icon}
                        <span>{ev.status}</span>
                      </span>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: '#94a3b8', maxWidth: '300px' }}>
                      {ev.rationale}
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
