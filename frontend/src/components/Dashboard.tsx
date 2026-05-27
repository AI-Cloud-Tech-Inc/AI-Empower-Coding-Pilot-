import { useCallback, useState } from 'react';
import { useApi } from '../hooks/useApi';
import { getHealth, runAdHoc } from '../services/api';
import type { PipelineResult } from '../types';

export default function Dashboard() {
  const { data: health } = useApi(useCallback(() => getHealth(), []));
  const [requirements, setRequirements] = useState('');
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    if (!requirements.trim()) return;
    setRunning(true);
    setError(null);
    try {
      const res = await runAdHoc(requirements);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setRunning(false);
    }
  };

  const features = [
    'AutoGen Multi-Agent',
    'Project Scaffolding',
    'CI/CD Generation',
    'Terraform IaC',
    'Docker Configs',
    'HIPAA/PCI/SOC2/GDPR',
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-500 mt-1">AI-Empower Autonomous Coding Pilot — Control Center</p>
      </div>

      {/* Status cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Status</p>
          <p className="text-2xl font-bold text-green-600 mt-1">{health?.status ?? '...'}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Version</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{health?.version ?? '...'}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Services</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">
            {health ? Object.keys(health.services).length : 0}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Agents</p>
          <p className="text-2xl font-bold text-purple-600 mt-1">6</p>
        </div>
      </div>

      {/* Feature badges */}
      <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-6 shadow-lg">
        <h3 className="text-white font-semibold mb-3">Platform Capabilities</h3>
        <div className="flex flex-wrap gap-2">
          {features.map((f) => (
            <span
              key={f}
              className="px-3 py-1 rounded-full text-xs font-medium bg-white/10 text-gray-200 border border-white/10"
            >
              {f}
            </span>
          ))}
        </div>
        <p className="text-gray-400 text-sm mt-3">
          83% more productive with parallel 6-agent orchestration
        </p>
      </div>

      {/* Quick run */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Pipeline Run</h3>
        <textarea
          value={requirements}
          onChange={(e) => setRequirements(e.target.value)}
          placeholder="Enter your project requirements..."
          className="w-full border border-gray-300 rounded-lg p-4 h-32 resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none text-sm"
        />
        <button
          onClick={handleRun}
          disabled={running || !requirements.trim()}
          className="mt-3 px-6 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm transition-all shadow-sm"
        >
          {running ? 'Running Pipeline...' : 'Run Pipeline'}
        </button>

        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-4 p-5 bg-gray-50 rounded-lg border border-gray-200">
            <h4 className="font-semibold text-gray-900 mb-3">Pipeline Result</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-gray-400 text-xs">Status</p>
                <p className={`font-semibold ${result.status === 'completed' ? 'text-green-600' : 'text-red-600'}`}>
                  {result.status}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-xs">Workflow</p>
                <p className="font-mono text-gray-700">{result.workflow_id.slice(0, 8)}...</p>
              </div>
              <div>
                <p className="text-gray-400 text-xs">Transitions</p>
                <p className="font-semibold text-gray-900">{result.transitions}</p>
              </div>
              <div>
                <p className="text-gray-400 text-xs">Duration</p>
                <p className="font-semibold text-gray-900">{result.duration_s.toFixed(3)}s</p>
              </div>
            </div>
            {result.errors.length > 0 && (
              <div className="mt-3 p-3 bg-red-50 rounded text-red-600 text-sm border border-red-100">
                {result.errors.map((e, i) => (
                  <div key={i}>{e}</div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
