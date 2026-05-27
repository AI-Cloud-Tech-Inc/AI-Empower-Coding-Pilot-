import { useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { listAgents } from '../services/api';

const ROLE_COLORS: Record<string, string> = {
  architect: 'bg-purple-100 text-purple-700',
  coder: 'bg-blue-100 text-blue-700',
  tester: 'bg-green-100 text-green-700',
  security: 'bg-red-100 text-red-700',
  docs: 'bg-yellow-100 text-yellow-700',
  reviewer: 'bg-indigo-100 text-indigo-700',
};

export default function AgentStatus() {
  const { data: agents, loading } = useApi(useCallback(() => listAgents(), []));

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Agent Status</h2>

      {loading && <p className="text-gray-500">Loading agents...</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents?.map((agent) => (
          <div key={agent.agent_id} className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between mb-2">
              <span
                className={`px-2 py-0.5 rounded text-xs font-medium ${ROLE_COLORS[agent.role] ?? 'bg-gray-100 text-gray-700'}`}
              >
                {agent.role}
              </span>
              <span className="inline-block w-2 h-2 rounded-full bg-green-500" title="idle" />
            </div>
            <p className="text-xs text-gray-400 font-mono">{agent.agent_id.slice(0, 12)}...</p>
            <p className="text-sm mt-1 text-gray-600 capitalize">{agent.status}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
