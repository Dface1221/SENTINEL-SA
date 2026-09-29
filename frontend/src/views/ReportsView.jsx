import React, { useEffect, useState } from 'react';
import { FileText, ExternalLink, Printer, Building, ShieldCheck } from 'lucide-react';
import { fetchCSEs, getExecutiveReportUrl, getCSEReportUrl } from '../api';

export default function ReportsView({ initialCSE = null }) {
  const [cses, setCses] = useState([]);
  const [selectedReport, setSelectedReport] = useState('executive');
  const [selectedCSE, setSelectedCSE] = useState(initialCSE);

  useEffect(() => {
    fetchCSEs().then(data => {
      setCses(data);
      if (data.length > 0 && !selectedCSE) {
        setSelectedCSE(data[0].cse_id);
      }
    }).catch(console.error);
  }, []);

  const reportUrl = selectedReport === 'executive'
    ? getExecutiveReportUrl()
    : getCSEReportUrl(selectedCSE);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Control Bar */}
      <div className="card" style={{ padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setSelectedReport('executive')}
              className={`btn ${selectedReport === 'executive' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.82rem' }}
            >
              <FileText size={15} />
              <span>National Executive Report</span>
            </button>

            <button
              onClick={() => setSelectedReport('cse')}
              className={`btn ${selectedReport === 'cse' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.82rem' }}
            >
              <Building size={15} />
              <span>CSE Audit Dossier</span>
            </button>
          </div>

          {selectedReport === 'cse' && (
            <select
              value={selectedCSE}
              onChange={(e) => setSelectedCSE(e.target.value)}
              style={{
                background: '#090d16',
                border: '1px solid var(--border-subtle)',
                color: '#f8fafc',
                padding: '6px 12px',
                borderRadius: '6px',
                fontSize: '0.82rem',
                fontWeight: '600'
              }}
            >
              {cses.map(c => (
                <option key={c.cse_id} value={c.cse_id}>
                  {c.cse_id} - {c.cse_name}
                </option>
              ))}
            </select>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <a
            href={reportUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary"
            style={{ fontSize: '0.82rem' }}
          >
            <ExternalLink size={15} />
            <span>Open in Fullscreen / Print PDF</span>
          </a>
        </div>
      </div>

      {/* Embedded Printable Report Preview Frame */}
      <div className="card" style={{ padding: '0', overflow: 'hidden', height: '760px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '10px 16px', background: '#0d1527', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.78rem', color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>
            PREVIEW: {selectedReport === 'executive' ? 'National Executive Supervisory Assessment' : `Audit Dossier for ${selectedCSE}`}
          </span>
          <span style={{ fontSize: '0.72rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <ShieldCheck size={14} /> Official Format Validated
          </span>
        </div>

        <iframe
          src={reportUrl}
          title="Supervisory Report"
          style={{ width: '100%', height: '100%', border: 'none', background: '#0b0f17' }}
        />
      </div>
    </div>
  );
}
