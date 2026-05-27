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

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Dashboard</h2>
        <p className="text-gray-500 text-sm">AI-Empower Coding Pilot Control Center</p>
      </div>

      {/* System status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">System Status</h3>
          <p className="text-2xl font-bold text-green-600">{health?.status ?? '...'}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Version</h3>
          <p className="text-2xl font-bold">{health?.version ?? '...'}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Services</h3>
          <p className="text-2xl font-bold">
            {health ? Object.keys(health.services).length : 0}
          </p>
        </div>
      </div>

      {/* Quick run */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-3">Quick Pipeline Run</h3>
        <textarea
          value={requirements}
          onChange={(e) => setRequirements(e.target.value)}
          placeholder="Enter your project requirements..."
          className="w-full border rounded-lg p-3 h-32 resize-none focus:ring-2 focus:ring-primary-500 focus:outline-none"
        />
        <button
          onClick={handleRun}
          disabled={running || !requirements.trim()}
          className="mt-3 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {running ? 'Running...' : 'Run Pipeline'}
        </button>

        {error && (
          <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">{error}</div>
        )}

        {result && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">Result</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-500">Status:</span>{' '}
                <span className={result.status === 'completed' ? 'text-green-600' : 'text-red-600'}>
                  {result.status}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Workflow:</span> {result.workflow_id.slice(0, 8)}...
              </div>
              <div>
                <span className="text-gray-500">Transitions:</span> {result.transitions}
              </div>
              <div>
                <span className="text-gray-500">Duration:</span> {result.duration_s.toFixed(3)}s
              </div>
            </div>
            {result.errors.length > 0 && (
              <div className="mt-2 text-red-600 text-sm">
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
