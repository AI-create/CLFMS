import { useState, useEffect, useCallback } from "react";
import {
  Users,
  Shield,
  ToggleLeft,
  ToggleRight,
  Trash2,
  RefreshCw,
} from "lucide-react";

const ROLE_COLORS = {
  admin: "bg-red-500/20 text-red-400 border-red-500/30",
  founder: "bg-purple-500/20 text-purple-400 border-purple-500/30",
  researcher: "bg-blue-500/20 text-blue-400 border-blue-500/30",
};

const VALID_ROLES = ["admin", "founder", "researcher"];

export default function SettingsPage({ user }) {
  const token = localStorage.getItem("token");
  const isAdmin = user?.role === "admin";

  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updating, setUpdating] = useState(null); // user id being updated

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/v1/users", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (res.ok) {
        setUsers(data.data || []);
      } else {
        setError(data.error?.message || "Failed to load users");
      }
    } catch {
      setError("Network error");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  async function updateUser(userId, payload) {
    setUpdating(userId);
    try {
      const res = await fetch(`/api/v1/users/${userId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (res.ok) {
        setUsers((prev) =>
          prev.map((u) => (u.id === userId ? { ...u, ...data.data } : u)),
        );
      } else {
        setError(data.error?.message || "Update failed");
      }
    } catch {
      setError("Network error");
    } finally {
      setUpdating(null);
    }
  }

  async function deleteUser(userId) {
    if (!window.confirm("Delete this user? This cannot be undone.")) return;
    setUpdating(userId);
    try {
      const res = await fetch(`/api/v1/users/${userId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (res.ok) {
        setUsers((prev) => prev.filter((u) => u.id !== userId));
      } else {
        setError(data.error?.message || "Delete failed");
      }
    } catch {
      setError("Network error");
    } finally {
      setUpdating(null);
    }
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Users className="w-6 h-6 text-blue-400" /> User Management
        </h1>
        <button
          onClick={fetchUsers}
          className="flex items-center gap-2 text-slate-400 hover:text-white border border-slate-600 hover:border-slate-400 rounded-lg px-3 py-2 text-sm transition-colors"
        >
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4 text-red-400 text-sm">
          {error}
        </div>
      )}

      <div className="bg-slate-800 border border-slate-700 rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400">Loading users…</div>
        ) : users.length === 0 ? (
          <div className="p-12 text-center text-slate-400">No users found.</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400 text-xs uppercase tracking-wider">
                <th className="text-left py-3 px-4">User</th>
                <th className="text-left py-3 px-4">Role</th>
                <th className="text-center py-3 px-4">Status</th>
                {isAdmin && <th className="text-right py-3 px-4">Actions</th>}
              </tr>
            </thead>
            <tbody>
              {users.map((u) => {
                const isSelf = u.id === user?.id;
                const busy = updating === u.id;
                return (
                  <tr
                    key={u.id}
                    className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors"
                  >
                    {/* User info */}
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-600/30 flex items-center justify-center text-blue-400 text-xs font-bold flex-shrink-0">
                          {(u.full_name || u.email)[0].toUpperCase()}
                        </div>
                        <div className="min-w-0">
                          <p className="text-white font-medium truncate">
                            {u.full_name || "—"}
                            {isSelf && (
                              <span className="ml-2 text-xs text-slate-500">
                                (you)
                              </span>
                            )}
                          </p>
                          <p className="text-slate-400 text-xs truncate">
                            {u.email}
                          </p>
                        </div>
                      </div>
                    </td>

                    {/* Role */}
                    <td className="py-3 px-4">
                      {isAdmin && !isSelf ? (
                        <select
                          value={u.role}
                          disabled={busy}
                          onChange={(e) =>
                            updateUser(u.id, { role: e.target.value })
                          }
                          className="bg-slate-700 border border-slate-600 text-white rounded-lg px-2 py-1 text-xs focus:outline-none focus:border-blue-500 disabled:opacity-50"
                        >
                          {VALID_ROLES.map((r) => (
                            <option key={r} value={r}>
                              {r}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-xs font-medium ${ROLE_COLORS[u.role] || "bg-slate-600 text-slate-300 border-slate-500"}`}
                        >
                          <Shield className="w-3 h-3" />
                          {u.role}
                        </span>
                      )}
                    </td>

                    {/* Status toggle */}
                    <td className="py-3 px-4 text-center">
                      {isAdmin && !isSelf ? (
                        <button
                          disabled={busy}
                          onClick={() =>
                            updateUser(u.id, { is_active: !u.is_active })
                          }
                          className="flex items-center gap-1.5 mx-auto text-xs disabled:opacity-50 transition-colors"
                          title={u.is_active ? "Deactivate" : "Activate"}
                        >
                          {u.is_active ? (
                            <>
                              <ToggleRight className="w-5 h-5 text-green-400" />
                              <span className="text-green-400">Active</span>
                            </>
                          ) : (
                            <>
                              <ToggleLeft className="w-5 h-5 text-slate-500" />
                              <span className="text-slate-500">Inactive</span>
                            </>
                          )}
                        </button>
                      ) : (
                        <span
                          className={`text-xs ${u.is_active ? "text-green-400" : "text-slate-500"}`}
                        >
                          {u.is_active ? "Active" : "Inactive"}
                        </span>
                      )}
                    </td>

                    {/* Delete */}
                    {isAdmin && (
                      <td className="py-3 px-4 text-right">
                        {!isSelf && (
                          <button
                            disabled={busy}
                            onClick={() => deleteUser(u.id)}
                            className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-50"
                            title="Delete user"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
