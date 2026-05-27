import type {
  Agent,
  AuditSummary,
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

// Cost (placeholder — no dedicated backend endpoint yet)
export const getCostReport = (): Promise<CostReport> =>
  Promise.resolve({
    total_tokens: 0,
    total_cost_usd: 0,
    budget_usd: 50,
    budget_remaining_usd: 50,
    budget_used_pct: 0,
    is_over_budget: false,
    recommendations: [],
  });
