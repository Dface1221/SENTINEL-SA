import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import DashboardView from './views/DashboardView';
import CSEsView from './views/CSEsView';
import CSEProfileView from './views/CSEProfileView';
import FindingsView from './views/FindingsView';
import ReviewQueueView from './views/ReviewQueueView';
import SamplesView from './views/SamplesView';
import NegativeSpaceView from './views/NegativeSpaceView';
import PeerBenchmarkView from './views/PeerBenchmarkView';
import RemediationView from './views/RemediationView';
import ValidationView from './views/ValidationView';
import ReportsView from './views/ReportsView';
import DataUploadView from './views/DataUploadView';
import FindingDetailModal from './views/FindingDetailModal';

export default function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const [selectedCSE, setSelectedCSE] = useState('CSE-07');
  const [selectedFindingId, setSelectedFindingId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleDataRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  const handleSelectCSE = (cseId) => {
    setSelectedCSE(cseId);
  };

  const handleSelectFinding = (findingId) => {
    setSelectedFindingId(findingId);
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        currentCSE={selectedCSE}
      />

      {/* Main Content Area */}
      <div className="main-content">
        <TopBar
          activeView={activeView}
          onDataRefresh={handleDataRefresh}
          onSelectCSE={handleSelectCSE}
        />

        <div className="content-body" key={refreshKey}>
          {activeView === 'dashboard' && (
            <DashboardView
              onNavigate={setActiveView}
              onSelectCSE={(id) => { setSelectedCSE(id); setActiveView('cse-profile'); }}
            />
          )}

          {activeView === 'cses' && (
            <CSEsView
              onSelectCSE={handleSelectCSE}
              onNavigate={setActiveView}
            />
          )}

          {activeView === 'cse-profile' && (
            <CSEProfileView
              cseId={selectedCSE}
              onSelectCSE={handleSelectCSE}
              onSelectFinding={handleSelectFinding}
              onNavigate={setActiveView}
            />
          )}

          {activeView === 'findings' && (
            <FindingsView
              onSelectFinding={handleSelectFinding}
            />
          )}

          {activeView === 'review-queue' && (
            <ReviewQueueView
              onSelectFinding={handleSelectFinding}
            />
          )}

          {activeView === 'samples' && (
            <SamplesView
              onSelectFinding={handleSelectFinding}
            />
          )}

          {activeView === 'negative-space' && (
            <NegativeSpaceView
              onSelectCSE={handleSelectCSE}
              onNavigate={setActiveView}
            />
          )}

          {activeView === 'benchmarks' && (
            <PeerBenchmarkView
              onSelectCSE={handleSelectCSE}
              onNavigate={setActiveView}
            />
          )}

          {activeView === 'remediation' && (
            <RemediationView />
          )}

          {activeView === 'validation' && (
            <ValidationView />
          )}

          {activeView === 'reports' && (
            <ReportsView
              initialCSE={selectedCSE}
            />
          )}

          {activeView === 'upload' && (
            <DataUploadView />
          )}
        </div>
      </div>

      {/* Modal for Finding Evidence & Decision */}
      {selectedFindingId && (
        <FindingDetailModal
          findingId={selectedFindingId}
          onClose={() => setSelectedFindingId(null)}
          onStatusUpdated={() => handleDataRefresh()}
        />
      )}
    </div>
  );
}
