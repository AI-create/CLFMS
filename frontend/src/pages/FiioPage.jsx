import { useState, useEffect, useCallback } from "react";
import { apiError } from "../utils/apiError";
import axios from "axios";
import {
  Plus,
  AlertCircle,
  Loader,
  TrendingUp,
  TrendingDown,
  RefreshCw,
  DollarSign,
  Clock,
  Zap,
  BarChart2,
  ChevronDown,
  ChevronUp,
  X,
  Trash2,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const API_URL = "/api/v1";
const TODAY = new Date().toISOString().split("T")[0];

const TABS = [
  { id: "overview", label: "Intelligence Overview" },
  { id: "hourly-incomes", label: "Hourly Income" },
  { id: "project-incomes", label: "Project Income" },
  { id: "hourly-expenses", label: "Hourly Expenses" },
  { id: "project-expenses", label: "Project Expenses" },
];

const PIE_COLORS = [
  "#6366f1",
  "#22c55e",
  "#f59e0b",
  "#ef4444",
  "#06b6d4",
  "#a855f7",
];

function KpiCard({ icon: Icon, label, value, sub, color = "indigo", trend }) {
  const colorMap = {
    indigo: "bg-indigo-50 text-indigo-600",
    green: "bg-green-50 text-green-600",
    red: "bg-red-50 text-red-600",
    amber: "bg-amber-50 text-amber-600",
    sky: "bg-sky-50 text-sky-600",
    purple: "bg-purple-50 text-purple-600",
  };
  return (
    <div className="card flex gap-4 items-start">
      <div className={`p-3 rounded-xl ${colorMap[color]}`}>
        <Icon size={22} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
        <p className="text-2xl font-bold text-gray-800 mt-0.5 truncate">
          {value}
        </p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
        {trend !== undefined && (
          <p
            className={`text-xs mt-1 flex items-center gap-1 ${trend >= 0 ? "text-green-600" : "text-red-500"}`}
          >
            {trend >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {Math.abs(trend)}% profit margin
          </p>
        )}
      </div>
    </div>
  );
}

function fmt(n) {
  if (n === undefined || n === null) return "\u2014";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(n);
}
function fmtHrs(n) {
  return `${(n || 0).toFixed(1)} hrs`;
}
function fmtPct(n) {
  return `${(n || 0).toFixed(1)}%`;
}

function OverviewTab() {
  const [intel, setIntel] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(30);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await axios.get(`${API_URL}/intelligence?days=${days}`);
      setIntel(res.data.data);
    } catch (err) {
      setError(apiError(err, "Failed to load intelligence data"));
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading)
    return (
      <div className="flex justify-center items-center h-48">
        <Loader className="animate-spin text-indigo-500" size={32} />
      </div>
    );
  if (error)
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex gap-2 text-red-700">
        <AlertCircle size={18} />
        {error}
      </div>
    );
  if (!intel) return null;

  const incomeData = (intel.income_breakdown || []).filter((d) => d.amount > 0);
  const expenseData = (intel.expense_breakdown || []).filter(
    (d) => d.amount > 0,
  );
  const categoryData = (intel.expense_by_category || []).filter(
    (d) => d.amount > 0,
  );
  const deptData = intel.department_earnings || [];
  const utilizationColor =
    intel.utilization_rate >= 75
      ? "green"
      : intel.utilization_rate >= 40
        ? "amber"
        : "red";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-700">
          Financial Intelligence &mdash; Last {days} days
        </h2>
        <div className="flex items-center gap-2">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="form-input py-1 text-sm w-32"
          >
            <option value={7}>7 days</option>
            <option value={30}>30 days</option>
            <option value={60}>60 days</option>
            <option value={90}>90 days</option>
            <option value={180}>180 days</option>
            <option value={365}>365 days</option>
          </select>
          <button
            onClick={load}
            className="btn-secondary flex items-center gap-1 py-1 text-sm"
          >
            <RefreshCw size={14} /> Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          icon={TrendingUp}
          label="Total Income"
          value={fmt(intel.total_income)}
          color="green"
        />
        <KpiCard
          icon={TrendingDown}
          label="Total Expense"
          value={fmt(intel.total_expense)}
          color="red"
        />
        <KpiCard
          icon={DollarSign}
          label="Net Profit"
          value={fmt(intel.net_profit)}
          color={intel.net_profit >= 0 ? "indigo" : "red"}
          trend={intel.profit_margin}
        />
        <KpiCard
          icon={BarChart2}
          label="Invoices Billed"
          value={fmt(intel.invoices_billed)}
          sub={`${fmt(intel.invoices_unpaid)} unpaid`}
          color="amber"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KpiCard
          icon={Clock}
          label="Effective Hourly Rate"
          value={fmt(intel.effective_hourly_rate)}
          sub={`Based on ${fmtHrs(intel.hours_billed)} billed`}
          color="sky"
        />
        <KpiCard
          icon={Zap}
          label="Hours Worked (Ops)"
          value={fmtHrs(intel.hours_worked_ops)}
          sub={`Attendance: ${fmtHrs(intel.hours_attendance)}`}
          color="purple"
        />
        <KpiCard
          icon={TrendingUp}
          label="Utilization Rate"
          value={fmtPct(intel.utilization_rate)}
          sub={`${intel.hours_billed} billed of ${intel.hours_worked_ops} worked hrs`}
          color={utilizationColor}
        />
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-700 mb-4 flex items-center gap-2">
          <Zap size={16} className="text-amber-500" /> Earning Potential
          Analysis
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-800">
              {intel.active_billable_employees}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Active Billable Employees
            </p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-800">
              {fmtHrs(intel.capacity_hours)}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Total Capacity (8h/day)
            </p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-indigo-600">
              {fmt(intel.potential_earnings)}
            </p>
            <p className="text-xs text-gray-500 mt-1">Max Potential Revenue</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-amber-600">
              {fmt(intel.unrealized_potential)}
            </p>
            <p className="text-xs text-gray-500 mt-1">Unrealized Potential</p>
          </div>
        </div>
        {intel.potential_earnings > 0 && (
          <div className="mt-4">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Actual Income: {fmt(intel.total_income)}</span>
              <span>Potential: {fmt(intel.potential_earnings)}</span>
            </div>
            <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-green-400 rounded-full transition-all"
                style={{
                  width: `${Math.min(100, (intel.total_income / intel.potential_earnings) * 100).toFixed(1)}%`,
                }}
              />
            </div>
            <p className="text-xs text-gray-400 mt-1 text-right">
              {((intel.total_income / intel.potential_earnings) * 100).toFixed(
                1,
              )}
              % of potential captured
            </p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {incomeData.length > 0 && (
          <div className="card">
            <h3 className="font-semibold text-gray-700 mb-4">Income Sources</h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={incomeData}
                  dataKey="amount"
                  nameKey="source"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ source, percent }) =>
                    `${source} ${(percent * 100).toFixed(0)}%`
                  }
                >
                  {incomeData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => fmt(v)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
        {expenseData.length > 0 && (
          <div className="card">
            <h3 className="font-semibold text-gray-700 mb-4">
              Expense Sources
            </h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={expenseData}
                  dataKey="amount"
                  nameKey="source"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ source, percent }) =>
                    `${source} ${(percent * 100).toFixed(0)}%`
                  }
                >
                  {expenseData.map((_, i) => (
                    <Cell
                      key={i}
                      fill={PIE_COLORS[(i + 2) % PIE_COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => fmt(v)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {categoryData.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-gray-700 mb-4">
            Expenses by Category
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={categoryData}
              layout="vertical"
              margin={{ left: 80 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" tickFormatter={(v) => fmt(v)} />
              <YAxis
                type="category"
                dataKey="category"
                width={80}
                tick={{ fontSize: 12 }}
              />
              <Tooltip formatter={(v) => fmt(v)} />
              <Bar dataKey="amount" fill="#ef4444" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {deptData.length > 0 && (
        <div className="card">
          <h3 className="font-semibold text-gray-700 mb-4">
            Department Earnings
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr>
                  <th className="table-th">Department</th>
                  <th className="table-th text-right">Income</th>
                  <th className="table-th text-right">Hours</th>
                  <th className="table-th text-right">Hourly Rate</th>
                </tr>
              </thead>
              <tbody>
                {deptData.map((d, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="table-td font-medium">{d.department}</td>
                    <td className="table-td text-right text-green-600">
                      {fmt(d.income)}
                    </td>
                    <td className="table-td text-right">{fmtHrs(d.hours)}</td>
                    <td className="table-td text-right text-indigo-600">
                      {fmt(d.hourly_rate)}/hr
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {incomeData.length === 0 &&
        expenseData.length === 0 &&
        deptData.length === 0 && (
          <div className="card text-center py-12 text-gray-400">
            <BarChart2 size={40} className="mx-auto mb-3 opacity-40" />
            <p className="font-medium">No financial data for this period</p>
            <p className="text-sm mt-1">
              Add invoices, payments, or expenses to see intelligence insights
            </p>
          </div>
        )}
    </div>
  );
}

const EMPTY_FORMS = {
  "hourly-incomes": {
    employee_id: "",
    project_id: "",
    client_id: "",
    income_date: TODAY,
    income_type: "hourly_billing",
    hours_billed: "",
    hourly_rate: "",
    description: "",
  },
  "project-incomes": {
    project_id: "",
    client_id: "",
    income_date: TODAY,
    income_type: "project_revenue",
    amount: "",
    description: "",
  },
  "hourly-expenses": {
    employee_id: "",
    project_id: "",
    expense_date: TODAY,
    expense_type: "salary",
    hours_worked: "",
    hourly_cost: "",
    description: "",
  },
  "project-expenses": {
    project_id: "",
    expense_date: TODAY,
    expense_type: "materials",
    amount: "",
    vendor: "",
    description: "",
  },
};

const INCOME_TYPES = [
  "hourly_billing",
  "project_revenue",
  "retainer",
  "milestone",
  "other",
];
const EXPENSE_TYPES = [
  "salary",
  "materials",
  "software",
  "travel",
  "overhead",
  "other",
];

function FormField({ label, children }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      {children}
    </div>
  );
}

function EntryModal({ tab, onClose, onSaved }) {
  const [form, setForm] = useState(EMPTY_FORMS[tab] || {});
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState(null);
  const [employees, setEmployees] = useState([]);
  const [projects, setProjects] = useState([]);
  const [clients, setClients] = useState([]);

  useEffect(() => {
    const loadLists = async () => {
      try {
        const [empRes, projRes, cliRes] = await Promise.all([
          axios.get(`${API_URL}/employees`),
          axios.get(`${API_URL}/projects`),
          axios.get(`${API_URL}/clients`),
        ]);
        setEmployees(empRes.data.data?.data || []);
        setProjects(projRes.data.data?.data || []);
        setClients(cliRes.data.data?.data || []);
      } catch {
        /* fallback to text inputs */
      }
    };
    loadLists();
  }, []);

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      setErr(null);
      const payload = {};
      Object.entries(form).forEach(([k, v]) => {
        if (v !== "") payload[k] = v;
      });
      await axios.post(`${API_URL}/${tab}`, payload);
      onSaved();
      onClose();
    } catch (ex) {
      setErr(apiError(ex, "Failed to save"));
    } finally {
      setSubmitting(false);
    }
  };

  const isIncome = tab.includes("income");
  const isHourly = tab.includes("hourly");

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-5 border-b">
          <h2 className="text-lg font-semibold text-gray-800">
            Add{" "}
            {tab.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
          </h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-lg"
          >
            <X size={18} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {err && (
            <div className="flex gap-2 text-red-600 bg-red-50 p-3 rounded-lg text-sm">
              <AlertCircle size={16} className="mt-0.5 shrink-0" />
              {err}
            </div>
          )}

          {"employee_id" in form && (
            <FormField label="Employee">
              <select
                value={form.employee_id}
                onChange={(e) => set("employee_id", e.target.value)}
                className="form-input"
              >
                <option value="">Select employee</option>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.name} ({emp.employee_id})
                  </option>
                ))}
              </select>
            </FormField>
          )}

          {"project_id" in form && (
            <FormField label="Project">
              <select
                value={form.project_id}
                onChange={(e) => set("project_id", e.target.value)}
                className="form-input"
              >
                <option value="">Select project</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </FormField>
          )}

          {"client_id" in form && (
            <FormField label="Client">
              <select
                value={form.client_id}
                onChange={(e) => set("client_id", e.target.value)}
                className="form-input"
              >
                <option value="">Select client</option>
                {clients.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </FormField>
          )}

          <FormField label={isIncome ? "Income Date" : "Expense Date"}>
            <input
              type="date"
              value={form.income_date || form.expense_date || ""}
              onChange={(e) =>
                set(isIncome ? "income_date" : "expense_date", e.target.value)
              }
              className="form-input"
              required
            />
          </FormField>

          <FormField label="Type">
            <select
              value={form.income_type || form.expense_type || ""}
              onChange={(e) =>
                set(isIncome ? "income_type" : "expense_type", e.target.value)
              }
              className="form-input"
            >
              {(isIncome ? INCOME_TYPES : EXPENSE_TYPES).map((t) => (
                <option key={t} value={t}>
                  {t.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </FormField>

          {isHourly && isIncome && (
            <div className="grid grid-cols-2 gap-4">
              <FormField label="Hours Billed">
                <input
                  type="number"
                  min="0"
                  step="0.5"
                  value={form.hours_billed}
                  onChange={(e) => set("hours_billed", e.target.value)}
                  className="form-input"
                  required
                />
              </FormField>
              <FormField label="Hourly Rate (INR)">
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.hourly_rate}
                  onChange={(e) => set("hourly_rate", e.target.value)}
                  className="form-input"
                  required
                />
              </FormField>
            </div>
          )}
          {isHourly && !isIncome && (
            <div className="grid grid-cols-2 gap-4">
              <FormField label="Hours Worked">
                <input
                  type="number"
                  min="0"
                  step="0.5"
                  value={form.hours_worked}
                  onChange={(e) => set("hours_worked", e.target.value)}
                  className="form-input"
                  required
                />
              </FormField>
              <FormField label="Hourly Cost (INR)">
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={form.hourly_cost}
                  onChange={(e) => set("hourly_cost", e.target.value)}
                  className="form-input"
                  required
                />
              </FormField>
            </div>
          )}

          {!isHourly && (
            <FormField label="Amount (INR)">
              <input
                type="number"
                min="0"
                step="0.01"
                value={form.amount}
                onChange={(e) => set("amount", e.target.value)}
                className="form-input"
                required
              />
            </FormField>
          )}

          {"vendor" in form && (
            <FormField label="Vendor">
              <input
                type="text"
                value={form.vendor}
                onChange={(e) => set("vendor", e.target.value)}
                className="form-input"
                placeholder="Vendor name"
              />
            </FormField>
          )}

          <FormField label="Description">
            <textarea
              rows={2}
              value={form.description}
              onChange={(e) => set("description", e.target.value)}
              className="form-input resize-none"
              placeholder="Optional notes..."
            />
          </FormField>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="btn-primary flex-1 flex items-center justify-center gap-2"
            >
              {submitting ? (
                <Loader size={16} className="animate-spin" />
              ) : (
                <Plus size={16} />
              )}
              {submitting ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ManualTab({ tab }) {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [expandedId, setExpandedId] = useState(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await axios.get(`${API_URL}/${tab}`);
      setRows(res.data.data?.data || []);
    } catch (err) {
      setError(apiError(err, "Failed to load data"));
    } finally {
      setLoading(false);
    }
  }, [tab]);

  useEffect(() => {
    load();
  }, [load]);

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this entry? This cannot be undone.")) return;
    try {
      await axios.delete(`${API_URL}/${tab}/${id}`);
      setRows(rows.filter((r) => r.id !== id));
    } catch (err) {
      alert(apiError(err, "Failed to delete entry"));
    }
  };

  const isIncome = tab.includes("income");
  const isHourly = tab.includes("hourly");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-gray-700">
          {tab.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}{" "}
          Records
        </h2>
        <button
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center gap-1 text-sm"
        >
          <Plus size={15} /> Add Entry
        </button>
      </div>

      {error && (
        <div className="flex gap-2 text-red-600 bg-red-50 p-3 rounded-lg text-sm">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-32">
          <Loader className="animate-spin text-indigo-500" size={28} />
        </div>
      ) : rows.length === 0 ? (
        <div className="card text-center py-12 text-gray-400">
          <p className="font-medium">No records found</p>
          <p className="text-sm mt-1">
            Click "Add Entry" to record your first entry
          </p>
        </div>
      ) : (
        <div className="card overflow-hidden p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="table-th">Date</th>
                  <th className="table-th">Type</th>
                  {isHourly && <th className="table-th text-right">Hours</th>}
                  {isHourly && <th className="table-th text-right">Rate</th>}
                  <th className="table-th text-right">Amount</th>
                  {!isIncome && <th className="table-th">Vendor</th>}
                  <th className="table-th w-8"></th>
                  <th className="table-th w-8"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {rows.map((row) => (
                  <>
                    <tr key={row.id} className="hover:bg-gray-50">
                      <td className="table-td">
                        {row.income_date || row.expense_date || "\u2014"}
                      </td>
                      <td className="table-td">
                        <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700">
                          {(
                            row.income_type ||
                            row.expense_type ||
                            "\u2014"
                          ).replace(/_/g, " ")}
                        </span>
                      </td>
                      {isHourly && (
                        <td className="table-td text-right">
                          {row.hours_billed || row.hours_worked || "\u2014"}
                        </td>
                      )}
                      {isHourly && (
                        <td className="table-td text-right">
                          {fmt(row.hourly_rate || row.hourly_cost)}
                        </td>
                      )}
                      <td
                        className={`table-td text-right font-semibold ${isIncome ? "text-green-600" : "text-red-500"}`}
                      >
                        {fmt(row.amount)}
                      </td>
                      {!isIncome && (
                        <td className="table-td">{row.vendor || "\u2014"}</td>
                      )}
                      <td className="table-td">
                        <button
                          onClick={() =>
                            setExpandedId(expandedId === row.id ? null : row.id)
                          }
                          className="text-gray-400 hover:text-gray-600"
                        >
                          {expandedId === row.id ? (
                            <ChevronUp size={15} />
                          ) : (
                            <ChevronDown size={15} />
                          )}
                        </button>
                      </td>
                      <td className="table-td">
                        <button
                          onClick={() => handleDelete(row.id)}
                          className="text-gray-300 hover:text-red-500 transition-colors"
                          title="Delete"
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                    {expandedId === row.id && (
                      <tr key={`${row.id}-exp`} className="bg-gray-50">
                        <td
                          colSpan={99}
                          className="px-4 py-2 text-sm text-gray-500"
                        >
                          {row.description || "No description"}
                          {row.employee_id && (
                            <span className="ml-4">
                              Employee ID: {row.employee_id}
                            </span>
                          )}
                          {row.project_id && (
                            <span className="ml-4">
                              Project ID: {row.project_id}
                            </span>
                          )}
                          {row.client_id && (
                            <span className="ml-4">
                              Client ID: {row.client_id}
                            </span>
                          )}
                        </td>
                      </tr>
                    )}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showModal && (
        <EntryModal
          tab={tab}
          onClose={() => setShowModal(false)}
          onSaved={load}
        />
      )}
    </div>
  );
}

export default function FiioPage() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          FI-IO &mdash; Financial Intelligence Income &amp; Outcomes
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          Auto-tracks income and expenses across all company functions &bull;
          Hourly earnings &bull; Earning potential
        </p>
      </div>

      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 overflow-x-auto">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              activeTab === tab.id
                ? "bg-white text-indigo-600 shadow-sm"
                : "text-gray-600 hover:text-gray-800"
            }`}
          >
            {tab.id === "overview" && (
              <Zap size={14} className="inline mr-1.5 mb-0.5" />
            )}
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "overview" ? (
        <OverviewTab />
      ) : (
        <ManualTab tab={activeTab} />
      )}
    </div>
  );
}
