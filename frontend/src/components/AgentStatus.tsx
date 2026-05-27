import { useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { listAgents } from '../services/api';

const ROLE_CONFIG: Record<string, { color: string; bg: string; desc: string }> = {
  architect: { color: 'text-purple-700', bg: 'bg-purple-100', desc: 'System design & architecture' },
  coder: { color: 'text-blue-700', bg: 'bg-blue-100', desc: 'Code generation & implementation' },
  tester: { color: 'text-green-700', bg: 'bg-green-100', desc: 'Test generation & execution' },
  security: { color: 'text-red-700', bg: 'bg-red-100', desc: 'SAST scanning & vulnerability detection' },
  docs: { color: 'text-amber-700', bg: 'bg-amber-100', desc: 'Auto-documentation generation' },
  reviewer: { color: 'text-indigo-700', bg: 'bg-indigo-100', desc: 'Code review & quality checks' },
};

export default function AgentStatus() {
  const { data: agents, loading } = useApi(useCallback(() => listAgents(), []));

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Agent Status</h2>
        <p className="text-gray-500 mt-1">6-agent parallel orchestration system — AutoGen group chat</p>
      </div>

      {loading && <p className="text-gray-500">Loading agents...</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {agents?.map((agent) => {
          const config = ROLE_CONFIG[agent.role] ?? { color: 'text-gray-700', bg: 'bg-gray-100', desc: '' };
          return (
            <div key={agent.agent_id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${config.bg} ${config.color}`}>
                  {agent.role.toUpperCase()}
                </span>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-xs text-gray-500 capitalize">{agent.status}</span>
                </div>
              </div>
              <p className="text-sm text-gray-600">{config.desc}</p>
              <p className="text-xs text-gray-400 font-mono mt-3">{agent.agent_id.slice(0, 16)}...</p>
            </div>
          );
        })}
      </div>

      {/* Orchestration info */}
      <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-6 shadow-lg">
        <h3 className="text-white font-semibold mb-2">AutoGen Group Chat Orchestration</h3>
        <p className="text-gray-400 text-sm">
          Agents collaborate through a shared message history with parallel execution stages.
          Stage 1: Architect (sequential) &rarr; Stage 2: Coder &rarr; Stage 3: Tester + Security (parallel) &rarr; Stage 4: Docs + Reviewer (parallel)
        </p>
      </div>
    </div>
  );
}
