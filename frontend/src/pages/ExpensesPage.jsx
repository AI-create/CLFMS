import { useState, useEffect } from "react";
import { apiError } from "../utils/apiError";
import axios from "axios";
import {
  Plus,
  AlertCircle,
  Loader,
  DollarSign,
  ChevronDown,
  ChevronRight,
  Folder,
  FolderOpen,
  X,
  Pencil,
  Trash2,
  Lock,
} from "lucide-react";
import { useProjectLocks } from "../hooks/useProjectLocks";

const API_URL = "/api/v1";

const CATEGORIES = [
  "salaries",
  "software",
  "hardware",
  "marketing",
  "travel",
  "utilities",
  "rent",
  "consulting",
  "materials",
  "other",
];

const EMPTY_FORM = {
  project_id: "",
  amount: "",
  category: "other",
  description: "",
  expense_date: new Date().toISOString().split("T")[0],
};

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [projects, setProjects] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingExpense, setEditingExpense] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const { getProjectLock } = useProjectLocks();
  const [filterCategory, setFilterCategory] = useState("");
  const [filterProject, setFilterProject] = useState("");
  const [expandedProjects, setExpandedProjects] = useState({});

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    fetchExpenses();
  }, [filterCategory, filterProject]);

  const fetchProjects = async () => {
    try {
      const res = await axios.get(`${API_URL}/projects`, {
        params: { limit: 200 },
      });
      setProjects(res.data?.data?.data || []);
    } catch {
      // non-fatal
    }
  };

  const fetchExpenses = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = { page: 1, limit: 500 };
      if (filterCategory) params.category = filterCategory;
      if (filterProject) params.project_id = filterProject;
      const response = await axios.get(`${API_URL}/expenses`, { params });
      const d = response.data.data;
      const rows = d?.data || [];
      setExpenses(rows);
      setTotal(d?.meta?.total || rows.length);
      setExpandedProjects((prev) => {
        const ids = {};
        rows.forEach((e) => {
          if (!(e.project_id in prev)) ids[e.project_id] = true;
        });
        return { ...ids, ...prev };
      });
    } catch (err) {
      setError(apiError(err, "Failed to load expenses"));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      const payload = {
        project_id: parseInt(form.project_id),
        amount: parseFloat(form.amount),
        category: form.category,
        description: form.description || null,
        expense_date: form.expense_date || null,
      };
      await axios.post(`${API_URL}/expenses`, payload);
      setShowModal(false);
      setForm(EMPTY_FORM);
      fetchExpenses();
    } catch (err) {
      alert(apiError(err, "Failed to create expense"));
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (expense) => {
    setEditingExpense({
      ...expense,
      project_id: String(expense.project_id),
      amount: String(expense.amount),
      expense_date: expense.expense_date || "",
      description: expense.description || "",
    });
    setShowEditModal(true);
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      const payload = {
        project_id: parseInt(editingExpense.project_id),
        amount: parseFloat(editingExpense.amount),
        category: editingExpense.category,
        description: editingExpense.description || null,
        expense_date: editingExpense.expense_date || null,
      };
      await axios.put(`${API_URL}/expenses/${editingExpense.id}`, payload);
      setShowEditModal(false);
      setEditingExpense(null);
      fetchExpenses();
    } catch (err) {
      alert(apiError(err, "Failed to update expense"));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this expense? This cannot be undone.")) return;
    try {
      setDeletingId(id);
      await axios.delete(`${API_URL}/expenses/${id}`);
      fetchExpenses();
    } catch (err) {
      alert(apiError(err, "Failed to delete expense"));
    } finally {
      setDeletingId(null);
    }
  };

  const projectName = (id) =>
    projects.find((p) => p.id === id)?.name || `Project #${id}`;

  const totalAmount = expenses.reduce((sum, e) => sum + (e.amount || 0), 0);

  const categoryTotals = expenses.reduce((acc, e) => {
    acc[e.category] = (acc[e.category] || 0) + (e.amount || 0);
    return acc;
  }, {});

  const grouped = expenses.reduce((acc, e) => {
    if (!acc[e.project_id]) acc[e.project_id] = [];
    acc[e.project_id].push(e);
    return acc;
  }, {});

  const toggleProject = (id) =>
    setExpandedProjects((prev) => ({ ...prev, [id]: !prev[id] }));

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Expenses</h1>
          <p className="text-gray-500 mt-1">Track project expenses and costs</p>
        </div>
        <button
          onClick={() => {
            setForm(EMPTY_FORM);
            setShowModal(true);
          }}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          Add Expense
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="card-lg">
          <p className="metric-label">Total Expenses</p>
          <p className="metric-value text-2xl text-red-600">
            ${totalAmount.toFixed(2)}
          </p>
          <p className="text-xs text-gray-400 mt-1">{total} records</p>
        </div>
        {Object.entries(categoryTotals)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 3)
          .map(([cat, amt]) => (
            <div key={cat} className="card-lg">
              <p className="metric-label capitalize">{cat}</p>
              <p className="metric-value text-2xl text-orange-600">
                ${(amt || 0).toFixed(2)}
              </p>
            </div>
          ))}
      </div>

      <div className="flex flex-wrap gap-4 mb-6">
        <select
          className="form-input w-52"
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
        >
          <option value="">All Categories</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c.charAt(0).toUpperCase() + c.slice(1)}
            </option>
          ))}
        </select>
        <select
          className="form-input w-52"
          value={filterProject}
          onChange={(e) => setFilterProject(e.target.value)}
        >
          <option value="">All Projects</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        {(filterCategory || filterProject) && (
          <button
            onClick={() => {
              setFilterCategory("");
              setFilterProject("");
            }}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800"
          >
            <X size={14} /> Clear filters
          </button>
        )}
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-48">
          <Loader className="animate-spin text-primary-600" size={28} />
        </div>
      ) : expenses.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-48 text-gray-400">
          <DollarSign size={48} className="mb-2 opacity-30" />
          <p>No expenses found. Add your first expense.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {Object.entries(grouped).map(([projectId, items]) => {
            const pid = parseInt(projectId);
            const isOpen = expandedProjects[pid] !== false;
            const projectTotal = items.reduce((s, e) => s + (e.amount || 0), 0);
            const name = projectName(pid);
            return (
              <div
                key={pid}
                className="border border-gray-200 rounded-xl overflow-hidden shadow-sm"
              >
                <button
                  onClick={() => toggleProject(pid)}
                  className="w-full flex items-center justify-between px-5 py-3 bg-gray-50 hover:bg-gray-100 transition text-left"
                >
                  <div className="flex items-center gap-3">
                    {isOpen ? (
                      <FolderOpen
                        size={20}
                        className="text-yellow-500 shrink-0"
                      />
                    ) : (
                      <Folder size={20} className="text-yellow-500 shrink-0" />
                    )}
                    <span className="font-semibold text-gray-800">{name}</span>
                    <span className="text-xs text-gray-400 bg-gray-200 rounded-full px-2 py-0.5">
                      {items.length} expense{items.length !== 1 ? "s" : ""}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-red-600">
                      ${projectTotal.toFixed(2)}
                    </span>
                    {isOpen ? (
                      <ChevronDown size={16} className="text-gray-400" />
                    ) : (
                      <ChevronRight size={16} className="text-gray-400" />
                    )}
                  </div>
                </button>
                {isOpen && (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="bg-white border-b border-gray-100">
                          <th className="table-th text-xs">Date</th>
                          <th className="table-th text-xs">Category</th>
                          <th className="table-th text-xs">Amount</th>
                          <th className="table-th text-xs">Description</th>
                          <th className="table-th text-xs">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-50">
                        {items.map((expense) => (
                          <tr key={expense.id} className="hover:bg-gray-50">
                            <td className="table-td text-sm text-gray-500">
                              {expense.expense_date || "\u2014"}
                            </td>
                            <td className="table-td">
                              <span className="badge badge-yellow capitalize text-xs">
                                {expense.category}
                              </span>
                            </td>
                            <td className="table-td text-red-600 font-semibold">
                              ${(expense.amount || 0).toFixed(2)}
                            </td>
                            <td className="table-td text-gray-500 text-sm">
                              {expense.description || "\u2014"}
                            </td>
                            <td className="table-td">
                              <div className="flex items-center gap-2">
                                {(() => {
                                  const lock = getProjectLock(
                                    expense.project_id,
                                  );
                                  return (
                                    <>
                                      <button
                                        onClick={() => {
                                          if (!lock.can_edit) return;
                                          handleEdit(expense);
                                        }}
                                        disabled={!lock.can_edit}
                                        title={
                                          !lock.can_edit
                                            ? `Project is ${lock.status} — editing disabled`
                                            : "Edit"
                                        }
                                        className={`p-1 rounded transition ${
                                          lock.can_edit
                                            ? "text-blue-500 hover:text-blue-700 hover:bg-blue-50"
                                            : "text-gray-400 cursor-not-allowed"
                                        }`}
                                      >
                                        {lock.locked && !lock.can_edit ? (
                                          <Lock size={14} />
                                        ) : (
                                          <Pencil size={14} />
                                        )}
                                      </button>
                                      <button
                                        onClick={() => {
                                          if (!lock.can_delete) return;
                                          handleDelete(expense.id);
                                        }}
                                        disabled={
                                          !lock.can_delete ||
                                          deletingId === expense.id
                                        }
                                        title={
                                          !lock.can_delete
                                            ? `Project is ${lock.status} — deletion disabled`
                                            : "Delete"
                                        }
                                        className={`p-1 rounded transition disabled:opacity-40 ${
                                          lock.can_delete
                                            ? "text-red-500 hover:text-red-700 hover:bg-red-50"
                                            : "text-gray-400 cursor-not-allowed"
                                        }`}
                                      >
                                        {lock.locked && !lock.can_delete ? (
                                          <Lock size={14} />
                                        ) : (
                                          <Trash2 size={14} />
                                        )}
                                      </button>
                                    </>
                                  );
                                })()}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                      <tfoot>
                        <tr className="bg-gray-50 border-t border-gray-100">
                          <td
                            colSpan={2}
                            className="table-td text-xs font-semibold text-gray-500"
                          >
                            Subtotal
                          </td>
                          <td className="table-td text-sm font-bold text-red-600">
                            ${projectTotal.toFixed(2)}
                          </td>
                          <td colSpan={2} />
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                )}
              </div>
            );
          })}
          <div className="flex justify-between items-center px-5 py-3 bg-red-50 border border-red-100 rounded-xl">
            <span className="font-semibold text-gray-700">Grand Total</span>
            <span className="text-xl font-bold text-red-600">
              ${totalAmount.toFixed(2)}
            </span>
          </div>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Add Expense</h2>
                <button
                  onClick={() => setShowModal(false)}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  <X size={18} />
                </button>
              </div>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="form-label">Project *</label>
                  <select
                    className="form-input"
                    required
                    value={form.project_id}
                    onChange={(e) =>
                      setForm({ ...form, project_id: e.target.value })
                    }
                  >
                    <option value="">Select a project</option>
                    {projects.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="form-label">Category *</label>
                  <select
                    className="form-input"
                    value={form.category}
                    onChange={(e) =>
                      setForm({ ...form, category: e.target.value })
                    }
                  >
                    {CATEGORIES.map((c) => (
                      <option key={c} value={c}>
                        {c.charAt(0).toUpperCase() + c.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="form-label">Amount ($) *</label>
                  <input
                    className="form-input"
                    type="number"
                    step="0.01"
                    min="0"
                    required
                    value={form.amount}
                    onChange={(e) =>
                      setForm({ ...form, amount: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="form-label">Expense Date</label>
                  <input
                    className="form-input"
                    type="date"
                    min={new Date().toISOString().split("T")[0]}
                    value={form.expense_date}
                    onChange={(e) =>
                      setForm({ ...form, expense_date: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="form-label">Description</label>
                  <textarea
                    className="form-input"
                    rows={2}
                    placeholder="Optional description"
                    value={form.description}
                    onChange={(e) =>
                      setForm({ ...form, description: e.target.value })
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
                    {submitting ? "Saving..." : "Save Expense"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
      {showEditModal && editingExpense && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Edit Expense</h2>
                <button
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingExpense(null);
                  }}
                  className="p-1 hover:bg-gray-100 rounded"
                >
                  <X size={18} />
                </button>
              </div>
              <form onSubmit={handleEditSubmit} className="space-y-4">
                <div>
                  <label className="form-label">Project *</label>
                  <select
                    className="form-input"
                    required
                    value={editingExpense.project_id}
                    onChange={(e) =>
                      setEditingExpense({
                        ...editingExpense,
                        project_id: e.target.value,
                      })
                    }
                  >
                    <option value="">Select a project</option>
                    {projects.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="form-label">Category *</label>
                  <select
                    className="form-input"
                    value={editingExpense.category}
                    onChange={(e) =>
                      setEditingExpense({
                        ...editingExpense,
                        category: e.target.value,
                      })
                    }
                  >
                    {CATEGORIES.map((c) => (
                      <option key={c} value={c}>
                        {c.charAt(0).toUpperCase() + c.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="form-label">Amount ($) *</label>
                  <input
                    className="form-input"
                    type="number"
                    step="0.01"
                    min="0"
                    required
                    value={editingExpense.amount}
                    onChange={(e) =>
                      setEditingExpense({
                        ...editingExpense,
                        amount: e.target.value,
                      })
                    }
                  />
                </div>
                <div>
                  <label className="form-label">Expense Date</label>
                  <input
                    className="form-input"
                    type="date"
                    min={new Date().toISOString().split("T")[0]}
                    value={editingExpense.expense_date}
                    onChange={(e) =>
                      setEditingExpense({
                        ...editingExpense,
                        expense_date: e.target.value,
                      })
                    }
                  />
                </div>
                <div>
                  <label className="form-label">Description</label>
                  <textarea
                    className="form-input"
                    rows={2}
                    placeholder="Optional description"
                    value={editingExpense.description}
                    onChange={(e) =>
                      setEditingExpense({
                        ...editingExpense,
                        description: e.target.value,
                      })
                    }
                  />
                </div>
                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => {
                      setShowEditModal(false);
                      setEditingExpense(null);
                    }}
                    className="btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="btn-primary flex-1"
                  >
                    {submitting ? "Saving..." : "Save Changes"}
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
