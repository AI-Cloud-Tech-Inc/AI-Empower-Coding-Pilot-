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
}

export interface CostReport {
  total_tokens: number;
  total_cost_usd: number;
  budget_usd: number;
  budget_remaining_usd: number;
  budget_used_pct: number;
  is_over_budget: boolean;
  recommendations: string[];
}

export interface AuditSummary {
  total_entries: number;
  event_counts: Record<string, number>;
}

export interface HealthStatus {
  status: string;
  version: string;
  services: Record<string, string>;
}
