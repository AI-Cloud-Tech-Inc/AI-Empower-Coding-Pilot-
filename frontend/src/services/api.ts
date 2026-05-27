import type {
  Agent,
  ApprovalReport,
  AuditSummary,
  AutoGenCapabilities,
  AutoGenResult,
  ComplianceReport,
  CostReport,
  HealthStatus,
  LLMGenerateResult,
  LLMStatus,
  PipelineResult,
  Project,
  TokenResponse,
} from '../types';

const BASE = '/api';

let authToken: string | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  const res = await fetch(`${BASE}${path}`, { headers, ...init });
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

// Auth
export const signup = (data: { username: string; email: string; password: string }) =>
  request<TokenResponse>('/auth/signup', { method: 'POST', body: JSON.stringify(data) });
export const login = (data: { username: string; password: string }) =>
  request<TokenResponse>('/auth/login', { method: 'POST', body: JSON.stringify(data) });

// LLM
export const getLLMStatus = () => request<LLMStatus>('/llm/status');
export const generateLLM = (prompt: string, agentRole?: string) =>
  request<LLMGenerateResult>('/llm/generate', {
    method: 'POST',
    body: JSON.stringify({ prompt, agent_role: agentRole ?? '' }),
  });

// Cost record
export const recordCostUsage = (tokens: number, model: string) =>
  request<{ recorded: boolean }>(`/cost/record?tokens=${tokens}&model=${encodeURIComponent(model)}`, {
    method: 'POST',
  });
