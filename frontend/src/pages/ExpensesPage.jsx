import { useState, useEffect } from "react";
import axios from "axios";
import { Plus, AlertCircle, Loader, DollarSign, Trash2 } from "lucide-react";

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
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [filterCategory, setFilterCategory] = useState("");
  const [filterProject, setFilterProject] = useState("");

  useEffect(() => {
    fetchExpenses();
  }, [filterCategory, filterProject]);

  const fetchExpenses = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = { page: 1, limit: 50 };
      if (filterCategory) params.category = filterCategory;
      if (filterProject) params.project_id = filterProject;
      const response = await axios.get(`${API_URL}/expenses`, { params });
      const d = response.data.data;
      setExpenses(d?.data || []);
      setTotal(d?.meta?.total || 0);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load expenses");
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
      alert(err.response?.data?.detail || "Failed to create expense");
    } finally {
      setSubmitting(false);
    }
  };

  const totalAmount = expenses.reduce((sum, e) => sum + (e.amount || 0), 0);

  const categoryTotals = expenses.reduce((acc, e) => {
    acc[e.category] = (acc[e.category] || 0) + (e.amount || 0);
    return acc;
  }, {});

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
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

      {/* Summary Cards */}
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

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-4">
        <select
          className="form-input w-48"
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
        <input
          className="form-input w-48"
          type="number"
          placeholder="Filter by Project ID"
          value={filterProject}
          onChange={(e) => setFilterProject(e.target.value)}
        />
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
        ) : expenses.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-gray-400">
            <DollarSign size={48} className="mb-2 opacity-30" />
            <p>No expenses found. Add your first expense.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="table-th">ID</th>
                  <th className="table-th">Date</th>
                  <th className="table-th">Project</th>
                  <th className="table-th">Category</th>
                  <th className="table-th">Amount</th>
                  <th className="table-th">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {expenses.map((expense) => (
                  <tr key={expense.id} className="hover:bg-gray-50">
                    <td className="table-td text-gray-500">{expense.id}</td>
                    <td className="table-td">{expense.expense_date || "—"}</td>
                    <td className="table-td">Project #{expense.project_id}</td>
                    <td className="table-td">
                      <span className="badge badge-yellow capitalize">
                        {expense.category}
                      </span>
                    </td>
                    <td className="table-td text-red-600 font-semibold">
                      ${(expense.amount || 0).toFixed(2)}
                    </td>
                    <td className="table-td text-gray-500 text-sm">
                      {expense.description || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="bg-gray-50 border-t border-gray-200">
                  <td
                    colSpan={4}
                    className="table-td font-semibold text-gray-700"
                  >
                    Total
                  </td>
                  <td className="table-td font-bold text-red-600">
                    ${totalAmount.toFixed(2)}
                  </td>
                  <td />
                </tr>
              </tfoot>
            </table>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">Add Expense</h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="form-label">Project ID *</label>
                  <input
                    className="form-input"
                    type="number"
                    required
                    min="1"
                    value={form.project_id}
                    onChange={(e) =>
                      setForm({ ...form, project_id: e.target.value })
                    }
                  />
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
                  <label className="form-label">Expense Date</label>
                  <input
                    className="form-input"
                    type="date"
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
    </div>
  );
}
