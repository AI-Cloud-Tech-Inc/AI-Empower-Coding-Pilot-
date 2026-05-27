import { useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { getAuditSummary } from '../services/api';

export default function AuditLog() {
  const { data: summary, loading } = useApi(useCallback(() => getAuditSummary(), []));

  if (loading) return <p className="text-gray-500">Loading audit log...</p>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Audit Log</h2>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-semibold mb-3">Summary</h3>
        <p className="text-3xl font-bold text-primary-600">{summary?.total_entries ?? 0}</p>
        <p className="text-sm text-gray-500">Total audit entries</p>
      </div>

      {summary && Object.keys(summary.event_counts).length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-3">Events by Type</h3>
          <div className="space-y-2">
            {Object.entries(summary.event_counts).map(([type, count]) => (
              <div key={type} className="flex justify-between items-center text-sm">
                <span className="font-mono text-gray-700">{type}</span>
                <span className="px-2 py-0.5 bg-gray-100 rounded text-gray-600">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
