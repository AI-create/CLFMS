import { useState, useEffect } from "react";
import axios from "axios";
import { AlertCircle, Loader, Activity } from "lucide-react";

const API_URL = "/api/v1";

const ACTIONS = [
  "create",
  "update",
  "delete",
  "upload",
  "download",
  "send",
  "approve",
  "reject",
  "login",
  "logout",
  "other",
];
const ENTITY_TYPES = [
  "client",
  "lead",
  "project",
  "task",
  "invoice",
  "payment",
  "employee",
  "document",
  "file",
  "hourly_income",
  "project_income",
  "hourly_expense",
  "project_expense",
];

const ACTION_COLORS = {
  create: "badge-green",
  update: "badge-blue",
  delete: "badge-red",
  upload: "badge-blue",
  download: "badge-blue",
  send: "badge-yellow",
  approve: "badge-green",
  reject: "badge-red",
  login: "badge-blue",
  logout: "badge-yellow",
};

export default function ActivityLogsPage() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [skip, setSkip] = useState(0);
  const limit = 20;
  const [filters, setFilters] = useState({
    action: "",
    entity_type: "",
    user_email: "",
    action_status: "",
  });

  useEffect(() => {
    fetchLogs();
  }, [skip, filters]);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = { skip, limit };
      if (filters.action) params.action = filters.action;
      if (filters.entity_type) params.entity_type = filters.entity_type;
      if (filters.user_email) params.user_email = filters.user_email;
      if (filters.action_status) params.action_status = filters.action_status;
      const response = await axios.get(`${API_URL}/activity-logs`, { params });
      const d = response.data.data;
      setLogs(d?.logs || []);
      setTotal(d?.total || 0);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load activity logs");
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters((prev) => ({ ...prev, [field]: value }));
    setSkip(0);
  };

  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(skip / limit) + 1;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Activity Logs</h1>
        <p className="text-gray-500 mt-1">Audit trail of all system actions</p>
      </div>

      {/* Filters */}
      <div className="card-lg mb-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <label className="form-label">Action</label>
          <select
            className="form-input"
            value={filters.action}
            onChange={(e) => handleFilterChange("action", e.target.value)}
          >
            <option value="">All Actions</option>
            {ACTIONS.map((a) => (
              <option key={a} value={a}>
                {a.charAt(0).toUpperCase() + a.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="form-label">Entity Type</label>
          <select
            className="form-input"
            value={filters.entity_type}
            onChange={(e) => handleFilterChange("entity_type", e.target.value)}
          >
            <option value="">All Entities</option>
            {ENTITY_TYPES.map((et) => (
              <option key={et} value={et}>
                {et.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="form-label">User Email</label>
          <input
            className="form-input"
            type="text"
            placeholder="Filter by email..."
            value={filters.user_email}
            onChange={(e) => handleFilterChange("user_email", e.target.value)}
          />
        </div>
        <div>
          <label className="form-label">Status</label>
          <select
            className="form-input"
            value={filters.action_status}
            onChange={(e) =>
              handleFilterChange("action_status", e.target.value)
            }
          >
            <option value="">All Statuses</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Table */}
      <div className="card overflow-hidden">
        {loading ? (
          <div className="flex justify-center items-center h-48">
            <Loader className="animate-spin text-primary-600" size={28} />
          </div>
        ) : logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-gray-400">
            <Activity size={48} className="mb-2 opacity-30" />
            <p>No activity logs found.</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-200">
                    <th className="table-th">Time</th>
                    <th className="table-th">User</th>
                    <th className="table-th">Action</th>
                    <th className="table-th">Entity</th>
                    <th className="table-th">Status</th>
                    <th className="table-th">Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {logs.map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="table-td text-gray-500 text-sm whitespace-nowrap">
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                      <td className="table-td text-sm">
                        {log.user_email || "—"}
                      </td>
                      <td className="table-td">
                        <span
                          className={`badge ${ACTION_COLORS[log.action] || "badge-blue"}`}
                        >
                          {log.action}
                        </span>
                      </td>
                      <td className="table-td text-sm">
                        {log.entity_type && (
                          <span className="text-gray-700">
                            {log.entity_type.replace(/_/g, " ")}
                            {log.entity_id ? ` #${log.entity_id}` : ""}
                            {log.entity_name ? ` — ${log.entity_name}` : ""}
                          </span>
                        )}
                      </td>
                      <td className="table-td">
                        <span
                          className={`badge ${log.action_status === "success" ? "badge-green" : "badge-red"}`}
                        >
                          {log.action_status}
                        </span>
                      </td>
                      <td className="table-td text-gray-500 text-sm max-w-xs truncate">
                        {log.description || "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                <p className="text-sm text-gray-500">
                  Showing {skip + 1}–{Math.min(skip + limit, total)} of {total}{" "}
                  logs
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setSkip(Math.max(0, skip - limit))}
                    disabled={skip === 0}
                    className="btn-secondary disabled:opacity-40"
                  >
                    Previous
                  </button>
                  <span className="px-3 py-2 text-sm text-gray-600">
                    Page {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={() => setSkip(skip + limit)}
                    disabled={skip + limit >= total}
                    className="btn-secondary disabled:opacity-40"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
