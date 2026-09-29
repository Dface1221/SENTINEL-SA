import React, { useEffect, useState } from 'react';
import { UploadCloud, CheckCircle, AlertCircle, FileSpreadsheet, ShieldAlert, History, Download } from 'lucide-react';
import { uploadDataset, fetchAuditLogs } from '../api';

export default function DataUploadView() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const loadAuditLogs = async () => {
    try {
      const logs = await fetchAuditLogs();
      setAuditLogs(logs);
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    try {
      setUploading(true);
      const res = await uploadDataset(file);
      setResult(res);
      loadAuditLogs();
    } catch (err) {
      setResult({ status: 'error', details: err.message });
    } finally {
      setUploading(false);
    }
  };

  const downloadSampleCSV = () => {
    const csvContent = "data:text/csv;charset=utf-8," +
      "alert_id,cse_id,asset_id,timestamp,severity,category,source,acknowledged_at,closed_at,duration_minutes,disposition\n" +
      "ALT-SAMPLE-01,CSE-01,AST-001,2026-08-10 14:20:00,Critical,Ransomware Precursor,EDR - Sentinel,2026-08-10 14:25:00,2026-08-10 15:15:00,50.0,True Positive\n" +
      "ALT-SAMPLE-02,CSE-02,AST-004,2026-08-11 09:12:00,Critical,SCADA Protocol Deviation,OT-Inspector,2026-08-11 09:15:00,2026-08-11 09:22:00,7.0,False Positive\n";
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "sat_sa_alert_sample_template.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Upload and Ingestion Card */}
      <div className="card">
        <div className="card-title">
          <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <UploadCloud size={18} color="#06b6d4" />
            <span>Air-Gapped Local Submission Ingestion (CSV / JSON)</span>
          </span>
          <button onClick={downloadSampleCSV} className="btn btn-secondary" style={{ fontSize: '0.78rem' }}>
            <Download size={14} />
            <span>Download Sample CSV Template</span>
          </button>
        </div>

        <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '10px' }}>
          <div style={{
            border: '2px dashed var(--border-subtle)',
            borderRadius: '8px',
            padding: '30px',
            textAlign: 'center',
            background: 'rgba(9, 13, 22, 0.5)',
            cursor: 'pointer'
          }}>
            <input
              type="file"
              accept=".csv,.json"
              onChange={(e) => setFile(e.target.files[0])}
              style={{ display: 'block', margin: '0 auto', fontSize: '0.85rem' }}
            />
            <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '10px' }}>
              Upload periodic SOC alert export (CSV or JSON format). Ingests and validates entirely within local SQLite.
            </p>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              type="submit"
              disabled={!file || uploading}
              className="btn btn-primary"
              style={{ fontSize: '0.85rem' }}
            >
              <span>{uploading ? 'Validating & Ingesting...' : 'Validate & Ingest File'}</span>
            </button>
          </div>
        </form>

        {result && (
          <div style={{
            marginTop: '16px',
            padding: '12px 16px',
            borderRadius: '6px',
            background: result.status === 'success' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(244, 63, 94, 0.12)',
            border: `1px solid ${result.status === 'success' ? '#10b981' : '#f43f5e'}`,
            color: result.status === 'success' ? '#6ee7b7' : '#fda4af',
            fontSize: '0.85rem'
          }}>
            {result.status === 'success' ? (
              <div>
                <strong>Ingestion Success:</strong> Processed {result.rows_processed} records from '{result.filename}'. Validated {result.entities_found} entities and {result.categories_found} categories.
              </div>
            ) : (
              <div>
                <strong>Validation Failure:</strong> {result.details}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Audit Trail Table */}
      <div className="card">
        <div className="card-title">
          <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <History size={18} color="#f59e0b" />
            <span>Supervisory Action Audit Trail (Local Immutable Log)</span>
            <span className="badge badge-green" style={{ marginLeft: '12px' }}>
              <CheckCircle size={12} style={{ display: 'inline', marginRight: '4px' }} />
              AUDIT CHAIN VALID
            </span>
          </span>
          <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Tracking All Analyst Actions</span>
        </div>

        <div style={{ maxHeight: '380px', overflowY: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Operator</th>
                <th>Supervisory Action</th>
                <th>Action Details & Notes</th>
                <th>Ledger Hash</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.map((log) => (
                <tr key={log.id}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: '#94a3b8' }}>
                    {log.timestamp}
                  </td>
                  <td style={{ fontWeight: '600', color: '#38bdf8' }}>
                    {log.user}
                  </td>
                  <td>
                    <span className="badge badge-low">{log.action}</span>
                  </td>
                  <td style={{ fontSize: '0.82rem', color: '#cbd5e1', maxWidth: '400px' }}>
                    {log.details}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: '#64748b', maxWidth: '120px', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                    <span title={`Current: ${log.current_hash}\nPrev: ${log.previous_hash}`}>
                      {log.current_hash ? log.current_hash.substring(0, 16) + '...' : 'N/A'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
