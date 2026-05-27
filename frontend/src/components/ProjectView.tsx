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
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Projects</h2>

      {/* Create */}
      <div className="bg-white rounded-lg shadow p-6 space-y-3">
        <h3 className="text-lg font-semibold">New Project</h3>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Project name"
          className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-primary-500 focus:outline-none"
        />
        <input
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
          placeholder="Description"
          className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-primary-500 focus:outline-none"
        />
        <textarea
          value={reqs}
          onChange={(e) => setReqs(e.target.value)}
          placeholder="Requirements"
          className="w-full border rounded-lg p-2 h-24 resize-none focus:ring-2 focus:ring-primary-500 focus:outline-none"
        />
        <button
          onClick={handleCreate}
          disabled={creating}
          className="px-5 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
        >
          {creating ? 'Creating...' : 'Create Project'}
        </button>
      </div>

      {/* List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b">
          <h3 className="font-semibold">All Projects</h3>
        </div>
        {projects && projects.length > 0 ? (
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left">Name</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Created</th>
                <th className="px-4 py-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((p) => (
                <tr key={p.id} className="border-t">
                  <td className="px-4 py-2 font-medium">{p.name}</td>
                  <td className="px-4 py-2">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
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
                  <td className="px-4 py-2 text-gray-500">
                    {new Date(p.created_at * 1000).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-2">
                    <button
                      onClick={() => handleRun(p.id)}
                      className="text-primary-600 hover:underline text-xs"
                    >
                      Run Pipeline
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="p-4 text-gray-500 text-sm">No projects yet.</p>
        )}
      </div>
    </div>
  );
}
