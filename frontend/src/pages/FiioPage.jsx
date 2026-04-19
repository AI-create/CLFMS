import { useState, useEffect } from "react";
import axios from "axios";
import {
  Plus,
  AlertCircle,
  Loader,
  TrendingUp,
  TrendingDown,
} from "lucide-react";

const API_URL = "/api/v1";

const TABS = [
  { id: "hourly-incomes", label: "Hourly Income" },
  { id: "project-incomes", label: "Project Income" },
  { id: "hourly-expenses", label: "Hourly Expenses" },
  { id: "project-expenses", label: "Project Expenses" },
];

const EMPTY_HOURLY_INCOME = {
  employee_id: "",
  project_id: "",
  client_id: "",
  income_date: new Date().toISOString().split("T")[0],
  income_type: "hourly_billing",
  hours_billed: "",
  hourly_rate: "",
  description: "",
};

const EMPTY_PROJECT_INCOME = {
  project_id: "",
  client_id: "",
  income_date: new Date().toISOString().split("T")[0],
  income_type: "project_revenue",
  amount: "",
  description: "",
};

const EMPTY_HOURLY_EXPENSE = {
  employee_id: "",
  project_id: "",
  expense_date: new Date().toISOString().split("T")[0],
  expense_type: "salary",
  hours_worked: "",
  hourly_cost: "",
  description: "",
};

const EMPTY_PROJECT_EXPENSE = {
  project_id: "",
  expense_date: new Date().toISOString().split("T")[0],
  expense_type: "materials",
  amount: "",
  vendor: "",
  description: "",
};

export default function FiioPage() {
  const [activeTab, setActiveTab] = useState("hourly-incomes");
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState(EMPTY_HOURLY_INCOME);

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const getEmptyForm = () => {
    if (activeTab === "hourly-incomes") return EMPTY_HOURLY_INCOME;
    if (activeTab === "project-incomes") return EMPTY_PROJECT_INCOME;
    if (activeTab === "hourly-expenses") return EMPTY_HOURLY_EXPENSE;
    return EMPTY_PROJECT_EXPENSE;
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_URL}/${activeTab}`);
      setData(response.data.data?.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      const payload = {};
      Object.entries(form).forEach(([k, v]) => {
        if (v !== "") payload[k] = v;
      });
      await axios.post(`${API_URL}/${activeTab}`, payload);
      setShowModal(false);
      setForm(getEmptyForm());
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to create record");
    } finally {
      setSubmitting(false);
    }
  };

  const openModal = () => {
    setForm(getEmptyForm());
    setShowModal(true);
  };

  const isIncome = activeTab.includes("income");

  const renderFormFields = () => {
    if (activeTab === "hourly-incomes") {
      return (
        <>
          <div>
            <label className="form-label">Employee ID *</label>
            <input
              className="form-input"
              type="number"
              required
              value={form.employee_id}
              onChange={(e) =>
                setForm({ ...form, employee_id: e.target.value })
              }
            />
          </div>
          <div>
            <label className="form-label">Project ID</label>
            <input
              className="form-input"
              type="number"
              value={form.project_id}
              onChange={(e) => setForm({ ...form, project_id: e.target.value })}
            />
          </div>
          <div>
            <label className="form-label">Client ID</label>
            <input
              className="form-input"
              type="number"
              value={form.client_id}
              onChange={(e) => setForm({ ...form, client_id: e.target.value })}
            />
          </div>
          <div>
            <label className="form-label">Income Date *</label>
            <input
              className="form-input"
              type="date"
              required
              value={form.income_date}
              onChange={(e) =>
                setForm({ ...form, income_date: e.target.value })
              }
            />
          </div>
          <div>
            <label className="form-label">Hours Billed *</label>
            <input
              className="form-input"
              type="number"
              step="0.25"
              min="0"
              required
              value={form.hours_billed}
              onChange={(e) =>
                setForm({ ...form, hours_billed: e.target.value })
              }
            />
          </div>
          <div>
            <label className="form-label">Hourly Rate ($) *</label>
            <input
              className="form-input"
              type="number"
              step="0.01"
              min="0"
              required
              value={form.hourly_rate}
              onChange={(e) =>
                setForm({ ...form, hourly_rate: e.target.value })
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
        </>
      );
    }
    if (activeTab === "project-incomes") {
      return (
        <>
          <div>
            <label className="form-label">Project ID *</label>
            <input
              className="form-input"
              type="number"
              required
              value={form.project_id}
              onChange={(e) => setForm({ ...form, project_id: e.target.value })}
            />
          </div>
          <div>
            <label className="form-label">Client ID *</label>
            <input
              className="form-input"
              type="number"
              required
              value={form.client_id}
              onChange={(e) => setForm({ ...form, client_id: e.target.value })}
            />
          </div>
          <div>
            <label className="form-label">Income Date *</label>
            <input
              className="form-input"
              type="date"
              required
              value={form.income_date}
              onChange={(e) =>
                setForm({ ...form, income_date: e.target.value })
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
              onChange={(e) => setForm({ ...form, amount: e.target.value })}
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
        </>
      );
    }
    if (activeTab === "hourly-expenses") {
      return (
        <>
          <div>
            <label className="form-label">Employee ID *</label>
            <input
              className="form-input"
              type="number"
              required
              value={form.employee_id}
              onChange={(e) =>
                setForm({ ...form, employee_id: e.target.value })
              }
            />
          </div>
          <div>
            <label className="form-label">Project ID</label>
            <input
              className="form-input"
              type="number"
              value={form.project_id}
              onChange={(e) => setForm({ ...form, project_id: e.target.value })}
            />
          </div>
          <div>
            <label className="form-label">Expense Date *</label>
            <input
              className="form-input"
              type="date"
              required
              value={form.expense_date}
              onChange={(e) =>
                setForm({ ...form, expense_date: e.target.value })
              }
            />
          </div>
          <div>
            <label className="form-label">Hours Worked *</label>
            <input
              className="form-input"
              type="number"
              step="0.25"
              min="0"
              required
              value={form.hours_worked}
              onChange={(e) =>
                setForm({ ...form, hours_worked: e.target.value })
              }
            />
          </div>
          <div>
            <label className="form-label">Hourly Cost ($) *</label>
            <input
              className="form-input"
              type="number"
              step="0.01"
              min="0"
              required
              value={form.hourly_cost}
              onChange={(e) =>
                setForm({ ...form, hourly_cost: e.target.value })
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
        </>
      );
    }
    // project-expenses
    return (
      <>
        <div>
          <label className="form-label">Project ID *</label>
          <input
            className="form-input"
            type="number"
            required
            value={form.project_id}
            onChange={(e) => setForm({ ...form, project_id: e.target.value })}
          />
        </div>
        <div>
          <label className="form-label">Expense Date *</label>
          <input
            className="form-input"
            type="date"
            required
            value={form.expense_date}
            onChange={(e) => setForm({ ...form, expense_date: e.target.value })}
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
            onChange={(e) => setForm({ ...form, amount: e.target.value })}
          />
        </div>
        <div>
          <label className="form-label">Vendor</label>
          <input
            className="form-input"
            type="text"
            placeholder="Optional vendor name"
            value={form.vendor}
            onChange={(e) => setForm({ ...form, vendor: e.target.value })}
          />
        </div>
        <div>
          <label className="form-label">Description</label>
          <textarea
            className="form-input"
            rows={2}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </div>
      </>
    );
  };

  const renderRow = (item) => {
    if (activeTab === "hourly-incomes") {
      return (
        <tr key={item.id}>
          <td className="table-td">{item.id}</td>
          <td className="table-td">{item.income_date}</td>
          <td className="table-td">Emp #{item.employee_id}</td>
          <td className="table-td">
            {item.hours_billed}h @ ${item.hourly_rate}/h
          </td>
          <td className="table-td text-green-600 font-semibold">
            ${(item.amount || 0).toFixed(2)}
          </td>
          <td className="table-td">
            <span className="badge badge-blue">{item.status}</span>
          </td>
          <td className="table-td text-gray-500 text-sm">
            {item.description || "—"}
          </td>
        </tr>
      );
    }
    if (activeTab === "project-incomes") {
      return (
        <tr key={item.id}>
          <td className="table-td">{item.id}</td>
          <td className="table-td">{item.income_date}</td>
          <td className="table-td">Project #{item.project_id}</td>
          <td className="table-td">Client #{item.client_id}</td>
          <td className="table-td text-green-600 font-semibold">
            ${(item.amount || 0).toFixed(2)}
          </td>
          <td className="table-td">
            <span className="badge badge-blue">{item.status}</span>
          </td>
          <td className="table-td text-gray-500 text-sm">
            {item.description || "—"}
          </td>
        </tr>
      );
    }
    if (activeTab === "hourly-expenses") {
      return (
        <tr key={item.id}>
          <td className="table-td">{item.id}</td>
          <td className="table-td">{item.expense_date}</td>
          <td className="table-td">Emp #{item.employee_id}</td>
          <td className="table-td">
            {item.hours_worked}h @ ${item.hourly_cost}/h
          </td>
          <td className="table-td text-red-600 font-semibold">
            ${(item.amount || 0).toFixed(2)}
          </td>
          <td className="table-td">
            <span className="badge badge-yellow">{item.status}</span>
          </td>
          <td className="table-td text-gray-500 text-sm">
            {item.description || "—"}
          </td>
        </tr>
      );
    }
    // project-expenses
    return (
      <tr key={item.id}>
        <td className="table-td">{item.id}</td>
        <td className="table-td">{item.expense_date}</td>
        <td className="table-td">Project #{item.project_id}</td>
        <td className="table-td text-red-600 font-semibold">
          ${(item.amount || 0).toFixed(2)}
        </td>
        <td className="table-td">
          <span className="badge badge-yellow">{item.status}</span>
        </td>
        <td className="table-td text-gray-500 text-sm">
          {item.description || "—"}
        </td>
      </tr>
    );
  };

  const getHeaders = () => {
    if (activeTab === "hourly-incomes")
      return [
        "ID",
        "Date",
        "Employee",
        "Hours × Rate",
        "Amount",
        "Status",
        "Description",
      ];
    if (activeTab === "project-incomes")
      return [
        "ID",
        "Date",
        "Project",
        "Client",
        "Amount",
        "Status",
        "Description",
      ];
    if (activeTab === "hourly-expenses")
      return [
        "ID",
        "Date",
        "Employee",
        "Hours × Rate",
        "Amount",
        "Status",
        "Description",
      ];
    return ["ID", "Date", "Project", "Amount", "Status", "Description"];
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">FI-IO Tracking</h1>
          <p className="text-gray-500 mt-1">
            Financial income and expense tracking
          </p>
        </div>
        <button
          onClick={openModal}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          Add Record
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition ${
              activeTab === tab.id
                ? "bg-white text-primary-700 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            {tab.label}
          </button>
        ))}
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
        ) : data.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-gray-400">
            {isIncome ? (
              <TrendingUp size={48} className="mb-2 opacity-30" />
            ) : (
              <TrendingDown size={48} className="mb-2 opacity-30" />
            )}
            <p>No records found. Add your first record.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  {getHeaders().map((h) => (
                    <th key={h} className="table-th">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.map((item) => renderRow(item))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">
                Add {TABS.find((t) => t.id === activeTab)?.label}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                {renderFormFields()}
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
                    {submitting ? "Saving..." : "Save"}
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
