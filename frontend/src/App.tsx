import { useState, useEffect } from 'react';
import { setAuthToken } from './services/api';
import type { UserResponse } from './types';
import AgentStatus from './components/AgentStatus';
import ApprovalPanel from './components/ApprovalPanel';
import AuditLog from './components/AuditLog';
import AutoGenPanel from './components/AutoGenPanel';
import CompliancePanel from './components/CompliancePanel';
import CostTracker from './components/CostTracker';
import Dashboard from './components/Dashboard';
import Layout from './components/Layout';
import LoginPage from './components/LoginPage';
import ProjectView from './components/ProjectView';
import Sidebar from './components/Sidebar';
import UserProfile from './components/UserProfile';

type Page =
  | 'dashboard'
  | 'projects'
  | 'agents'
  | 'autogen'
  | 'compliance'
  | 'approvals'
  | 'audit'
  | 'cost'
  | 'profile';

export default function App() {
  const [page, setPage] = useState<Page>('dashboard');
  const [user, setUser] = useState<UserResponse | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    if (storedToken && storedUser) {
      setAuthToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleLogin = (loggedInUser: UserResponse) => {
    setUser(loggedInUser);
  };

  const handleLogout = () => {
    setAuthToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setPage('dashboard');
  };

  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  const renderPage = () => {
    switch (page) {
      case 'dashboard':
        return <Dashboard />;
      case 'projects':
        return <ProjectView />;
      case 'agents':
        return <AgentStatus />;
      case 'autogen':
        return <AutoGenPanel />;
      case 'compliance':
        return <CompliancePanel />;
      case 'approvals':
        return <ApprovalPanel />;
      case 'audit':
        return <AuditLog />;
      case 'cost':
        return <CostTracker />;
      case 'profile':
        return <UserProfile user={user} onLogout={handleLogout} />;
    }
  };

  return (
    <Layout sidebar={<Sidebar current={page} onNavigate={setPage} user={user} onLogout={handleLogout} />}>
      {renderPage()}
    </Layout>
  );
}
