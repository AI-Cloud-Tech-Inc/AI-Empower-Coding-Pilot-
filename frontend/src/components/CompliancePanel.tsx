import { useCallback } from 'react';
import { useApi } from '../hooks/useApi';
import { getCompliance } from '../services/api';

export default function CompliancePanel() {
  const { data: report, loading } = useApi(useCallback(() => getCompliance(), []));

  if (loading) return <p className="text-gray-500">Loading compliance report...</p>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Compliance</h2>

      {/* Overall status */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center gap-3">
          <div
            className={`w-4 h-4 rounded-full ${report?.compliant ? 'bg-green-500' : 'bg-red-500'}`}
          />
          <span className="text-lg font-semibold">
            {report?.compliant ? 'All Compliant' : 'Violations Found'}
          </span>
        </div>
        <p className="text-sm text-gray-500 mt-1">
          {report?.total_violations ?? 0} violation(s) across all frameworks
        </p>
      </div>

      {/* Framework cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {(['hipaa', 'pci', 'soc2'] as const).map((fw) => {
          const data = report?.[fw] as Record<string, unknown> | undefined;
          const compliant = (data?.compliant as boolean) ?? true;
          const violations = (data?.violations as unknown[]) ?? [];

          return (
            <div key={fw} className="bg-white rounded-lg shadow p-4">
              <h3 className="font-semibold uppercase text-sm text-gray-700">{fw}</h3>
              <p className={`text-lg font-bold ${compliant ? 'text-green-600' : 'text-red-600'}`}>
                {compliant ? 'Compliant' : `${violations.length} Violation(s)`}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
