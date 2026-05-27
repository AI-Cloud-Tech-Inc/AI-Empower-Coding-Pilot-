import { useCallback, useState } from 'react';
import { useApi } from '../hooks/useApi';
import { createProject, listProjects, runPipeline } from '../services/api';

export default function ProjectView() {
  const { data: projects, refetch } = useApi(useCallback(() => listProjects(), []));
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [reqs, setReqs] = useState('');
  const [creating, setCreating] = useState(false);

  const handleCreate = async () => {
    if (!name.trim() || !reqs.trim()) return;
    setCreating(true);
    try {
      await createProject({ name, description: desc, requirements: reqs });
      setName('');
      setDesc('');
      setReqs('');
      refetch();
    } finally {
      setCreating(false);
    }
  };

  const handleRun = async (id: string) => {
    await runPipeline(id);
    refetch();
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Projects</h2>
        <p className="text-gray-500 mt-1">Manage and run AI-powered development pipelines</p>
      </div>

      {/* Create */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">New Project</h3>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Project name"
          className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none text-sm"
        />
        <input
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
          placeholder="Description"
          className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none text-sm"
        />
        <textarea
          value={reqs}
          onChange={(e) => setReqs(e.target.value)}
          placeholder="Requirements"
          className="w-full border border-gray-300 rounded-lg px-4 py-2.5 h-24 resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none text-sm"
        />
        <button
          onClick={handleCreate}
          disabled={creating}
          className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 font-medium text-sm transition-all shadow-sm"
        >
          {creating ? 'Creating...' : 'Create Project'}
        </button>
      </div>

      {/* List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-5 border-b border-gray-200">
          <h3 className="font-semibold text-gray-900">All Projects</h3>
        </div>
        {projects && projects.length > 0 ? (
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {projects.map((p) => (
                <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-5 py-3 font-medium text-gray-900">{p.name}</td>
                  <td className="px-5 py-3">
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                        p.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : p.status === 'failed'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-yellow-100 text-yellow-700'
                      }`}
                    >
                      {p.status}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-gray-500">
                    {new Date(p.created_at * 1000).toLocaleDateString()}
                  </td>
                  <td className="px-5 py-3">
                    <button
                      onClick={() => handleRun(p.id)}
                      className="px-3 py-1 bg-blue-50 text-blue-700 rounded text-xs font-medium hover:bg-blue-100 transition-colors"
                    >
                      Run Pipeline
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="p-5 text-gray-500 text-sm">No projects yet. Create one above.</p>
        )}
      </div>
    </div>
  );
}
