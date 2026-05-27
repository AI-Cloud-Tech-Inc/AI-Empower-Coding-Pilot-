import type { UserResponse } from '../types';

interface UserProfileProps {
  user: UserResponse;
  onLogout: () => void;
}

export default function UserProfile({ user, onLogout }: UserProfileProps) {
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">User Profile</h2>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 max-w-lg">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white text-2xl font-bold">
            {user.username[0].toUpperCase()}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{user.username}</h3>
            <p className="text-sm text-gray-500">{user.email}</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-sm text-gray-500">User ID</span>
            <span className="text-sm font-mono text-gray-700">{user.id.slice(0, 8)}...</span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-sm text-gray-500">Role</span>
            <span className="text-sm font-medium px-2.5 py-0.5 bg-blue-100 text-blue-700 rounded-full capitalize">
              {user.role}
            </span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-sm text-gray-500">Status</span>
            <span className={`text-sm font-medium px-2.5 py-0.5 rounded-full ${
              user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>
              {user.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>

        <button
          onClick={onLogout}
          className="mt-6 w-full py-2.5 bg-red-50 text-red-600 rounded-lg font-medium hover:bg-red-100 transition-colors border border-red-200"
        >
          Sign Out
        </button>
      </div>
    </div>
  );
}
