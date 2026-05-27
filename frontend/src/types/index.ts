export interface Project {
  id: string;
  name: string;
  description: string;
  status: string;
  created_at: number;
  updated_at: number;
}

export interface Agent {
  role: string;
  agent_id: string;
  status: string;
}

export interface PipelineResult {
  workflow_id: string;
  status: string;
  data: Record<string, unknown>;
  errors: string[];
  transitions: number;
  duration_s: number;
}

export interface ComplianceReport {
  status: string;
  compliant: boolean;
  total_violations: number;
  hipaa: Record<string, unknown>;
  pci: Record<string, unknown>;
  soc2: Record<string, unknown>;
  gdpr: Record<string, unknown>;
}

export interface CostReport {
  total_tokens: number;
  total_cost_usd: number;
  budget_usd: number;
  budget_remaining_usd: number;
  budget_used_pct: number;
  is_over_budget: boolean;
  alert_triggered: boolean;
  total_records: number;
  recommendations: string[];
}

export interface AuditSummary {
  total_entries: number;
  event_counts: Record<string, number>;
  integrity: {
    valid: boolean;
    entries_checked: number;
  };
}

export interface HealthStatus {
  status: string;
  version: string;
  services: Record<string, string>;
}

export interface ApprovalReport {
  total_requests: number;
  pending: number;
  approved: number;
  rejected: number;
  gates: string[];
  requests: Record<string, unknown>[];
}

export interface AutoGenResult {
  scaffolding: { files: string[]; count: number };
  cicd: { files: string[]; count: number };
  docker: { files: string[]; count: number };
  terraform: { files: string[]; count: number };
  total_files_generated: number;
}

export interface AutoGenCapabilities {
  engines: {
    name: string;
    description: string;
    templates?: string[];
    platforms?: string[];
    runtimes?: string[];
    providers?: string[];
  }[];
}

export interface UserResponse {
  id: string;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserResponse;
}

export interface LLMStatus {
  provider: string;
  model: string;
  api_key_configured: boolean;
}

export interface LLMGenerateResult {
  content: string;
  model: string;
  tokens_used: number;
  latency_ms: number;
  cached: boolean;
}
