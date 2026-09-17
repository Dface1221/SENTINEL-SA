import React, { useState } from 'react';
import { Database, Play, CheckCircle, AlertTriangle, Shield, RefreshCw } from 'lucide-react';
import { generateDemoData, runSupervisoryAnalysis } from '../api';

export default function TopBar({ activeView, onDataRefresh, onSelectCSE }) {
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 4000);
  };

  const handleGenerateData = async () => {
    try {
      setLoading(true);
      const res = await generateDemoData();
      showToast(`Generated ${res.generator_result.alerts_count.toLocaleString()} alerts across ${res.generator_result.cses_count} CSEs!`, 'success');
      onDataRefresh();
    } catch (err) {
      showToast(`Generation failed: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRunAnalysis = async () => {
    try {
      setLoading(true);
      const res = await runSupervisoryAnalysis();
      showToast(`Supervisory analysis complete: ${res.total_findings} findings detected!`, 'success');
      onDataRefresh();
    } catch (err) {
      showToast(`Analysis failed: ${err.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const viewTitles = {
    'dashboard': 'National SOC Supervisory Command Dashboard',
    'cses': 'Critical Sector Entities (CSEs) Directory',
    'cse-profile': 'Entity Operational Resilience & Supervisory Profile',
    'findings': 'Supervisory Findings & Evidence Explorer',
    'review-queue': 'Prioritized Manual Supervisory Review Queue',
    'samples': 'Intelligent Alert Sample Prioritization',
    'negative-space': 'Negative Space & Operational Blind Spot Matrix',
    'benchmarks': 'Sector Peer Benchmarking & Percentile Distribution Hub',
    'remediation': '"Heal the Wound" Supervisory Remediation Tracker',
    'validation': 'Empirical Analytics Validation (Ground Truth vs Algorithmic Review)',
    'reports': 'Official Supervisory Reports & Dossier Generator',
    'upload': 'Data Ingestion, CSV Validation & Audit Trail'
  };

  return (
    <header className="top-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: '700', color: '#f8fafc', letterSpacing: '-0.01em' }}>
          {viewTitles[activeView] || 'Supervisory Assessment'}
        </h2>
        {activeView === 'dashboard' && (
          <span className="badge badge-blue" style={{ fontSize: '0.7rem' }}>
            PERIOD: 2026-Q3
          </span>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        {/* Toast Notification */}
        {toast && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: toast.type === 'error' ? 'rgba(244, 63, 94, 0.2)' : 'rgba(16, 185, 129, 0.2)',
            border: `1px solid ${toast.type === 'error' ? '#f43f5e' : '#10b981'}`,
            color: toast.type === 'error' ? '#fda4af' : '#6ee7b7',
            padding: '6px 14px',
            borderRadius: '6px',
            fontSize: '0.82rem',
            fontWeight: '500'
          }}>
            {toast.type === 'error' ? <AlertTriangle size={15} /> : <CheckCircle size={15} />}
            {toast.msg}
          </div>
        )}

        {/* Action 1: Generate Demo Dataset */}
        <button
          onClick={handleGenerateData}
          disabled={loading}
          className="btn btn-secondary"
          title="Generates 12 CSEs with 16,000+ realistic alerts, cases, assets and ground truth"
        >
          <Database size={15} color="#38bdf8" />
          <span>Generate Demo Dataset</span>
        </button>

        {/* Action 2: Run Supervisory Analysis */}
        <button
          onClick={handleRunAnalysis}
          disabled={loading}
          className="btn btn-primary"
          title="Executes execution gaps, negative space, peer benchmarks, and risk scoring"
        >
          {loading ? <RefreshCw size={15} className="spin" /> : <Play size={15} />}
          <span>Run Supervisory Analysis</span>
        </button>

        {/* Role Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 12px', background: 'rgba(255, 255, 255, 0.04)', border: '1px solid var(--border-subtle)', borderRadius: '6px' }}>
          <Shield size={16} color="#06b6d4" />
          <div style={{ fontSize: '0.78rem' }}>
            <span style={{ color: '#f8fafc', fontWeight: '600' }}>Supervisor</span>
            <span style={{ color: '#64748b', marginLeft: '6px' }}>NCIIPC Lead</span>
          </div>
        </div>
      </div>
    </header>
  );
}
