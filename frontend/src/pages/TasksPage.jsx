import { useState, useEffect } from "react";
import { apiError } from "../utils/apiError";
import axios from "axios";
import {
  Plus,
  Edit,
  Trash2,
  AlertCircle,
  Loader,
  Search,
  CheckCircle,
  Clock,
  X,
  Lock,
} from "lucide-react";
import TaskForm from "../components/TaskForm";
import { useProjectLocks } from "../hooks/useProjectLocks";

const API_URL = "/api/v1";

export default function TasksPage() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [timeLogTask, setTimeLogTask] = useState(null);
  const [timeLogForm, setTimeLogForm] = useState({
    hours: "",
    log_date: "",
    notes: "",
  });
  const [timeLogSaving, setTimeLogSaving] = useState(false);
  const { getProjectLock } = useProjectLocks();

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/tasks`);
      setTasks(response.data.data?.data || []);
      setError(null);
    } catch (err) {
      console.error("Error fetching tasks:", err);
      setError(apiError(err, "Failed to load tasks"));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;

    try {
      await axios.delete(`${API_URL}/tasks/${id}`);
      setTasks(tasks.filter((t) => t.id !== id));
    } catch (err) {
      setError(apiError(err, "Failed to delete task"));
    }
  };

  const handleLogTime = async (e) => {
    e.preventDefault();
    try {
      setTimeLogSaving(true);
      const payload = {
        task_id: timeLogTask.id,
        hours: parseFloat(timeLogForm.hours),
      };
      if (timeLogForm.log_date) payload.log_date = timeLogForm.log_date;
      if (timeLogForm.notes) payload.notes = timeLogForm.notes;
      await axios.post(`${API_URL}/time-logs`, payload);
      setTimeLogTask(null);
      setTimeLogForm({ hours: "", log_date: "", notes: "" });
    } catch (err) {
      setError(apiError(err, "Failed to log time"));
    } finally {
      setTimeLogSaving(false);
    }
  };

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch =
      !searchTerm ||
      task.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.description?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus =
      statusFilter === "all" || task.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
        <button
          onClick={() => {
            setEditingTask(null);
            setShowForm(true);
          }}
          className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          <Plus size={20} />
          New Task
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Task Form Modal */}
      {showForm && (
        <TaskForm
          task={editingTask}
          onClose={() => {
            setShowForm(false);
            setEditingTask(null);
          }}
          onSave={() => {
            setShowForm(false);
            setEditingTask(null);
            fetchTasks();
          }}
        />
      )}

      {/* Filters */}
      <div className="flex gap-4 items-center">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-3 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search tasks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="all">All Status</option>
          <option value="todo">Todo</option>
          <option value="in_progress">In Progress</option>
          <option value="done">Done</option>
        </select>
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      ) : filteredTasks.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No tasks found</p>
        </div>
      ) : (
        /* Tasks List */
        <div className="grid gap-4">
          {filteredTasks.map((task) => (
            <div
              key={task.id}
              className="bg-white p-4 rounded-lg shadow border border-gray-200 hover:shadow-md transition"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {task.title}
                    </h3>
                    <span
                      className={`px-2 py-1 rounded text-sm font-medium ${
                        task.status === "done"
                          ? "bg-green-100 text-green-800"
                          : task.status === "in_progress"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-yellow-100 text-yellow-800"
                      }`}
                    >
                      {task.status}
                    </span>
                  </div>
                  {task.description && (
                    <p className="text-gray-600 mt-2">{task.description}</p>
                  )}
                  <div className="flex gap-4 mt-3 text-sm text-gray-500">
                    {task.assigned_to && (
                      <span>Assigned to: User #{task.assigned_to}</span>
                    )}
                    {task.estimated_hours && (
                      <span>Est: {task.estimated_hours}h</span>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  {(() => {
                    const lock = getProjectLock(task.project_id);
                    return (
                      <>
                        <button
                          onClick={() => {
                            setTimeLogTask(task);
                            setTimeLogForm({
                              hours: "",
                              log_date: "",
                              notes: "",
                            });
                          }}
                          className="p-2 text-purple-600 hover:bg-purple-50 rounded"
                          title="Log Time"
                        >
                          <Clock size={20} />
                        </button>
                        <button
                          onClick={() => {
                            if (!lock.can_edit) return;
                            setEditingTask(task);
                            setShowForm(true);
                          }}
                          disabled={!lock.can_edit}
                          title={
                            !lock.can_edit
                              ? `Project is ${lock.status} — editing disabled`
                              : "Edit"
                          }
                          className={`p-2 rounded ${
                            lock.can_edit
                              ? "text-blue-600 hover:bg-blue-50"
                              : "text-gray-400 cursor-not-allowed bg-gray-50"
                          }`}
                        >
                          {lock.locked && !lock.can_edit ? (
                            <Lock size={20} />
                          ) : (
                            <Edit size={20} />
                          )}
                        </button>
                        <button
                          onClick={() => {
                            if (!lock.can_delete) return;
                            handleDelete(task.id);
                          }}
                          disabled={!lock.can_delete}
                          title={
                            !lock.can_delete
                              ? `Project is ${lock.status} — deletion disabled`
                              : "Delete"
                          }
                          className={`p-2 rounded ${
                            lock.can_delete
                              ? "text-red-600 hover:bg-red-50"
                              : "text-gray-400 cursor-not-allowed bg-gray-50"
                          }`}
                        >
                          {lock.locked && !lock.can_delete ? (
                            <Lock size={20} />
                          ) : (
                            <Trash2 size={20} />
                          )}
                        </button>
                      </>
                    );
                  })()}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      {/* Time Log Modal */}
      {timeLogTask && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-sm">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">
                  Log Time â€” {timeLogTask.title}
                </h2>
                <button
                  onClick={() => setTimeLogTask(null)}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  <X size={18} />
                </button>
              </div>
              <form onSubmit={handleLogTime} className="space-y-3">
                <div>
                  <label className="form-label">Hours *</label>
                  <input
                    className="form-input"
                    type="number"
                    step="0.25"
                    min="0.25"
                    required
                    value={timeLogForm.hours}
                    onChange={(e) =>
                      setTimeLogForm({ ...timeLogForm, hours: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="form-label">Date</label>
                  <input
                    className="form-input"
                    type="date"
                    min={new Date().toISOString().split("T")[0]}
                    value={timeLogForm.log_date}
                    onChange={(e) =>
                      setTimeLogForm({
                        ...timeLogForm,
                        log_date: e.target.value,
                      })
                    }
                  />
                </div>
                <div>
                  <label className="form-label">Notes</label>
                  <textarea
                    className="form-input"
                    rows={2}
                    value={timeLogForm.notes}
                    onChange={(e) =>
                      setTimeLogForm({ ...timeLogForm, notes: e.target.value })
                    }
                  />
                </div>
                <div className="flex gap-3 pt-1">
                  <button
                    type="button"
                    onClick={() => setTimeLogTask(null)}
                    className="btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={timeLogSaving}
                    className="btn-primary flex-1"
                  >
                    {timeLogSaving ? "Saving..." : "Log Time"}
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
