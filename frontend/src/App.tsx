import { useState } from 'react';
import AgentStatus from './components/AgentStatus';
import AuditLog from './components/AuditLog';
import CompliancePanel from './components/CompliancePanel';
import CostTracker from './components/CostTracker';
import Dashboard from './components/Dashboard';
import Layout from './components/Layout';
import ProjectView from './components/ProjectView';
import Sidebar from './components/Sidebar';

type Page = 'dashboard' | 'projects' | 'agents' | 'compliance' | 'audit' | 'cost';

export default function App() {
  const [page, setPage] = useState<Page>('dashboard');

  const renderPage = () => {
    switch (page) {
      case 'dashboard':
        return <Dashboard />;
      case 'projects':
        return <ProjectView />;
      case 'agents':
        return <AgentStatus />;
      case 'compliance':
        return <CompliancePanel />;
      case 'audit':
        return <AuditLog />;
      case 'cost':
        return <CostTracker />;
    }
  };

  return (
    <Layout sidebar={<Sidebar current={page} onNavigate={setPage} />}>
      {renderPage()}
    </Layout>
  );
}
