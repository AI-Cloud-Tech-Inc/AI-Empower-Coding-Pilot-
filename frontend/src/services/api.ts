import type {
  Agent,
  ApprovalReport,
  AuditSummary,
  AutoGenCapabilities,
  AutoGenResult,
  ComplianceReport,
  CostReport,
  HealthStatus,
  PipelineResult,
  Project,
} from '../types';

const BASE = '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

// Health
export const getHealth = () => request<HealthStatus>('/health');

// Projects
export const listProjects = () => request<Project[]>('/projects');
export const createProject = (data: { name: string; description: string; requirements: string }) =>
  request<Project>('/projects', { method: 'POST', body: JSON.stringify(data) });
export const runPipeline = (projectId: string) =>
  request<PipelineResult>(`/projects/${projectId}/run`, { method: 'POST' });
export const runAdHoc = (requirements: string) =>
  request<PipelineResult>('/projects/run', {
    method: 'POST',
    body: JSON.stringify({ requirements }),
  });

// Agents
export const listAgents = () => request<Agent[]>('/agents');

// Compliance
export const getCompliance = () => request<ComplianceReport>('/compliance');

// Audit
export const getAuditSummary = () => request<AuditSummary>('/audit/summary');

// Cost
export const getCostReport = () => request<CostReport>('/cost');

// Approvals
export const getApprovals = () => request<ApprovalReport>('/approvals');

// Auto-generation
export const generateAll = (architecture: Record<string, unknown>, projectName: string) =>
  request<AutoGenResult>('/autogen/generate', {
    method: 'POST',
    body: JSON.stringify({ architecture, project_name: projectName }),
  });

export const getAutoGenCapabilities = () => request<AutoGenCapabilities>('/autogen/capabilities');
