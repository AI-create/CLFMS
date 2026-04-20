import { useState, useEffect } from "react";
import { apiError } from "../utils/apiError";
import axios from "axios";
import { Plus, Edit, AlertCircle, Loader, ClipboardList } from "lucide-react";

const API_URL = "/api/v1";

const STATUSES = [
  "assigned",
  "in_progress",
  "completed",
  "cancelled",
  "on_hold",
];
const PRIORITIES = ["low", "medium", "high", "urgent"];

const STATUS_COLORS = {
  assigned: "badge-yellow",
  in_progress: "badge-blue",
  completed: "badge-green",
  cancelled: "badge-red",
  on_hold: "badge-yellow",
};

const PRIORITY_COLORS = {
  low: "badge-blue",
  medium: "badge-yellow",
  high: "badge-red",
  urgent: "badge-red",
};

const EMPTY_FORM = {
  title: "",
  description: "",
  assigned_to_id: "",
  project_id: "",
  priority: "medium",
  estimated_hours: "",
  due_date: "",
  start_date: "",
  notes: "",
};

export default function OperationsPage() {
  const [assignments, setAssignments] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [filterStatus, setFilterStatus] = useState("");
  const [filterPriority, setFilterPriority] = useState("");

  useEffect(() => {
    fetchEmployees();
  }, []);

  useEffect(() => {
    fetchAssignments();
  }, [filterStatus, filterPriority]);

  const fetchEmployees = async () => {
    try {
      const res = await axios.get(`${API_URL}/employees`, {
        params: { limit: 200 },
      });
      setEmployees(res.data?.data?.data || []);
    } catch {
      // non-critical
    }
  };

  const fetchAssignments = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = { page: 1, limit: 50 };
      if (filterStatus) params.status = filterStatus;
      if (filterPriority) params.priority = filterPriority;
      const response = await axios.get(`${API_URL}/task-assignments`, {
        params,
      });
      const d = response.data.data;
      setAssignments(d?.data || []);
      setTotal(d?.meta?.total || 0);
    } catch (err) {
      setError(apiError(err, "Failed to load task assignments"));
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setForm(EMPTY_FORM);
    setEditingId(null);
    setShowModal(true);
  };

  const handleEdit = (task) => {
    setForm({
      title: task.title || "",
      description: task.description || "",
      assigned_to_id: task.assigned_to_id?.toString() || "",
      project_id: task.project_id?.toString() || "",
      priority: task.priority || "medium",
      estimated_hours: task.estimated_hours?.toString() || "",
      due_date: task.due_date || "",
      start_date: task.start_date || "",
      notes: task.notes || "",
    });
    setEditingId(task.id);
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      const payload = {
        title: form.title,
        priority: form.priority,
        assigned_to_id: parseInt(form.assigned_to_id),
      };
      if (form.description) payload.description = form.description;
      if (form.project_id) payload.project_id = parseInt(form.project_id);
      if (form.estimated_hours)
        payload.estimated_hours = parseFloat(form.estimated_hours);
      if (form.due_date) payload.due_date = form.due_date;
      if (form.start_date) payload.start_date = form.start_date;
      if (form.notes) payload.notes = form.notes;

      if (editingId) {
        await axios.put(`${API_URL}/task-assignments/${editingId}`, payload);
      } else {
        await axios.post(`${API_URL}/task-assignments`, payload);
      }
      setShowModal(false);
      fetchAssignments();
    } catch (err) {
      alert(apiError(err, "Operation failed"));
    } finally {
      setSubmitting(false);
    }
  };

  const handleStatusUpdate = async (taskId, newStatus) => {
    try {
      await axios.put(`${API_URL}/task-assignments/${taskId}`, {
        status: newStatus,
      });
      setAssignments(
        assignments.map((t) =>
          t.id === taskId ? { ...t, status: newStatus } : t,
        ),
      );
    } catch (err) {
      alert(apiError(err, "Failed to update status"));
    }
  };

  const pendingCount = assignments.filter(
    (t) => t.status === "assigned",
  ).length;
  const inProgressCount = assignments.filter(
    (t) => t.status === "in_progress",
  ).length;
  const completedCount = assignments.filter(
    (t) => t.status === "completed",
  ).length;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Operations</h1>
          <p className="text-gray-500 mt-1">
            Task assignments and employee workload
          </p>
        </div>
        <button
          onClick={handleCreate}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          Assign Task
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-8">
        <div className="card-lg">
          <p className="metric-label">Total Assignments</p>
          <p className="metric-value text-2xl">{total}</p>
        </div>
        <div className="card-lg">
          <p className="metric-label">Assigned</p>
          <p className="metric-value text-2xl text-yellow-600">
            {pendingCount}
          </p>
        </div>
        <div className="card-lg">
          <p className="metric-label">In Progress</p>
          <p className="metric-value text-2xl text-blue-600">
            {inProgressCount}
          </p>
        </div>
        <div className="card-lg">
          <p className="metric-label">Completed</p>
          <p className="metric-value text-2xl text-green-600">
            {completedCount}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-4">
        <select
          className="form-input w-48"
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
        >
          <option value="">All Statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s.replace(/_/g, " ")}
            </option>
          ))}
        </select>
        <select
          className="form-input w-48"
          value={filterPriority}
          onChange={(e) => setFilterPriority(e.target.value)}
        >
          <option value="">All Priorities</option>
          {PRIORITIES.map((p) => (
            <option key={p} value={p}>
              {p.charAt(0).toUpperCase() + p.slice(1)}
            </option>
          ))}
        </select>
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
        ) : assignments.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-gray-400">
            <ClipboardList size={48} className="mb-2 opacity-30" />
            <p>No task assignments found. Create the first one.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="table-th">Title</th>
                  <th className="table-th">Assigned To</th>
                  <th className="table-th">Project</th>
                  <th className="table-th">Priority</th>
                  <th className="table-th">Status</th>
                  <th className="table-th">Due Date</th>
                  <th className="table-th">Progress</th>
                  <th className="table-th">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {assignments.map((task) => (
                  <tr key={task.id} className="hover:bg-gray-50">
                    <td className="table-td">
                      <div>
                        <p className="font-medium text-gray-900">
                          {task.title}
                        </p>
                        {task.description && (
                          <p className="text-xs text-gray-500 truncate max-w-xs">
                            {task.description}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="table-td text-gray-600">
                      {employees.find((e) => e.id === task.assigned_to_id)
                        ?.name || `Emp #${task.assigned_to_id}`}
                    </td>
                    <td className="table-td text-gray-500">
                      {task.project_id ? `Project #${task.project_id}` : "â€”"}
                    </td>
                    <td className="table-td">
                      <span
                        className={`badge ${PRIORITY_COLORS[task.priority] || "badge-blue"}`}
                      >
                        {task.priority}
                      </span>
                    </td>
                    <td className="table-td">
                      <select
                        className="text-xs border border-gray-200 rounded px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-primary-500"
                        value={task.status}
                        onChange={(e) =>
                          handleStatusUpdate(task.id, e.target.value)
                        }
                      >
                        {STATUSES.map((s) => (
                          <option key={s} value={s}>
                            {s.replace(/_/g, " ")}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="table-td text-gray-500 text-sm">
                      {task.due_date || "â€”"}
                    </td>
                    <td className="table-td">
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full"
                            style={{
                              width: `${task.completed_percentage || 0}%`,
                            }}
                          />
                        </div>
                        <span className="text-xs text-gray-500">
                          {(task.completed_percentage || 0).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="table-td">
                      <button
                        onClick={() => handleEdit(task)}
                        className="text-primary-600 hover:text-primary-800"
                        title="Edit"
                      >
                        <Edit size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">
                {editingId ? "Edit Task Assignment" : "Assign Task"}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="form-label">Title *</label>
                  <input
                    className="form-input"
                    type="text"
                    required
                    value={form.title}
                    onChange={(e) =>
                      setForm({ ...form, title: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="form-label">Assign To *</label>
                  <select
                    className="form-input"
                    required
                    value={form.assigned_to_id}
                    onChange={(e) =>
                      setForm({ ...form, assigned_to_id: e.target.value })
                    }
                  >
                    <option value="">Select employeeâ€¦</option>
                    {employees.map((emp) => (
                      <option key={emp.id} value={emp.id}>
                        {emp.name} ({emp.employee_id})
                      </option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="form-label">Priority</label>
                    <select
                      className="form-input"
                      value={form.priority}
                      onChange={(e) =>
                        setForm({ ...form, priority: e.target.value })
                      }
                    >
                      {PRIORITIES.map((p) => (
                        <option key={p} value={p}>
                          {p.charAt(0).toUpperCase() + p.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="form-label">Project ID</label>
                    <input
                      className="form-input"
                      type="number"
                      min="1"
                      value={form.project_id}
                      onChange={(e) =>
                        setForm({ ...form, project_id: e.target.value })
                      }
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="form-label">Start Date</label>
                    <input
                      className="form-input"
                      type="date"
                      min={new Date().toISOString().split("T")[0]}
                      value={form.start_date}
                      onChange={(e) =>
                        setForm({ ...form, start_date: e.target.value })
                      }
                    />
                  </div>
                  <div>
                    <label className="form-label">Due Date</label>
                    <input
                      className="form-input"
                      type="date"
                      min={new Date().toISOString().split("T")[0]}
                      value={form.due_date}
                      onChange={(e) =>
                        setForm({ ...form, due_date: e.target.value })
                      }
                    />
                  </div>
                </div>
                <div>
                  <label className="form-label">Estimated Hours</label>
                  <input
                    className="form-input"
                    type="number"
                    step="0.5"
                    min="0"
                    value={form.estimated_hours}
                    onChange={(e) =>
                      setForm({ ...form, estimated_hours: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="form-label">Description</label>
                  <textarea
                    className="form-input"
                    rows={2}
                    value={form.description}
                    onChange={(e) =>
                      setForm({ ...form, description: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="form-label">Notes</label>
                  <textarea
                    className="form-input"
                    rows={2}
                    value={form.notes}
                    onChange={(e) =>
                      setForm({ ...form, notes: e.target.value })
                    }
                  />
                </div>
                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="btn-primary flex-1"
                  >
                    {submitting
                      ? "Saving..."
                      : editingId
                        ? "Update"
                        : "Assign Task"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
