import { useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { getAuditSummary } from '../services/api';

export default function AuditLog() {
  const { data: summary, loading } = useApi(useCallback(() => getAuditSummary(), []));

  if (loading) return <p className="text-gray-500">Loading audit log...</p>;

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Audit Log</h2>
        <p className="text-gray-500 mt-1">Immutable cryptographic audit trail with SHA-256 hash chain</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Total Entries</p>
          <p className="text-3xl font-bold text-blue-600 mt-1">{summary?.total_entries ?? 0}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Event Types</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">
            {summary ? Object.keys(summary.event_counts).length : 0}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">Integrity</p>
          <p className={`text-3xl font-bold mt-1 ${summary?.integrity?.valid !== false ? 'text-green-600' : 'text-red-600'}`}>
            {summary?.integrity?.valid !== false ? 'Valid' : 'Broken'}
          </p>
        </div>
      </div>

      {summary && Object.keys(summary.event_counts).length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Events by Type</h3>
          <div className="space-y-3">
            {Object.entries(summary.event_counts).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <span className="font-mono text-sm text-gray-700">{type}</span>
                <span className="px-3 py-1 bg-gray-100 rounded-full text-sm font-medium text-gray-600">
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hash chain info */}
      <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-6 shadow-lg">
        <h3 className="text-white font-semibold mb-2">Cryptographic Hash Chain</h3>
        <p className="text-gray-400 text-sm">
          Each audit entry is linked to the previous via SHA-256 hash, forming an immutable chain.
          Any tampering breaks the chain and is detectable via integrity verification.
        </p>
        {summary?.integrity && (
          <p className="text-gray-300 text-sm mt-2">
            Entries verified: {summary.integrity.entries_checked}
          </p>
        )}
      </div>
    </div>
  );
}
