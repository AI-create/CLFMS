import { useState, useEffect } from "react";
import { apiError } from "../utils/apiError";
import axios from "axios";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { AlertCircle, Loader, Download } from "lucide-react";

const API_URL = "/api/v1";

export default function FinancialReportsPage() {
  const [financialSummary, setFinancialSummary] = useState(null);
  const [profitTrend, setProfitTrend] = useState(null);
  const [topProjects, setTopProjects] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchReportData();
  }, []);

  const fetchReportData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [finRes, trendRes, projRes] = await Promise.all([
        axios.get(`${API_URL}/dashboard/financial-summary`),
        axios.get(`${API_URL}/dashboard/profit-trend`),
        axios.get(`${API_URL}/dashboard/top-projects`),
      ]);

      setFinancialSummary(finRes.data);
      setProfitTrend(trendRes.data);
      setTopProjects(projRes.data);
    } catch (err) {
      console.error("Error fetching report data:", err);
      setError(apiError(err, "Failed to load reports"));
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

  const handleExportPDF = () => {
    window.print();
  };

  const handleExportCSV = () => {
    const summary = financialSummary?.data;
    const trendData = profitTrend?.data?.data || [];
    const projectData = topProjects?.data?.data || [];

    let csv = "Financial Summary\n";
    if (summary) {
      csv += `Total Income,${summary.total_income}\n`;
      csv += `Total Expense,${summary.total_expense}\n`;
      csv += `Net Profit,${summary.total_profit}\n`;
      csv += `Profit Margin,${summary.profit_margin}%\n\n`;
    }

    csv += "30-Day Profit Trend\nDate,Income,Expense,Profit\n";
    trendData.forEach((d) => {
      csv += `${d.date},${d.income},${d.expense},${d.profit}\n`;
    });

    csv += "\nTop Projects\nProject,Income,Expense,Profit,Margin\n";
    projectData.forEach((p) => {
      csv += `${p.project_name},${p.income},${p.expense},${p.profit},${p.margin}%\n`;
    });

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `financial-report-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Financial Reports</h1>
        <div className="flex gap-2">
          <button
            onClick={handleExportPDF}
            className="btn-secondary flex items-center gap-2"
          >
            <Download size={20} />
            Export PDF
          </button>
          <button
            onClick={handleExportCSV}
            className="btn-secondary flex items-center gap-2"
          >
            <Download size={20} />
            Export CSV
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-96">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      ) : (
        <>
          {/* Summary Metrics */}
          {financialSummary?.data && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="card-lg">
                <p className="metric-label">Total Income</p>
                <p className="metric-value text-2xl text-green-600">
                  ${(financialSummary.data.total_income || 0).toFixed(2)}
                </p>
              </div>
              <div className="card-lg">
                <p className="metric-label">Total Expenses</p>
                <p className="metric-value text-2xl text-orange-600">
                  ${(financialSummary.data.total_expense || 0).toFixed(2)}
                </p>
              </div>
              <div className="card-lg">
                <p className="metric-label">Net Profit</p>
                <p className="metric-value text-2xl text-blue-600">
                  ${(financialSummary.data.total_profit || 0).toFixed(2)}
                </p>
              </div>
              <div className="card-lg">
                <p className="metric-label">Profit Margin</p>
                <p className="metric-value text-2xl text-primary-600">
                  {(financialSummary.data.profit_margin || 0).toFixed(1)}%
                </p>
              </div>
            </div>
          )}

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Income vs Expenses Breakdown Chart */}
            {financialSummary?.data && (
              <div className="card-lg">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Income vs Expenses by Category
                </h2>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={[
                        {
                          category: "Legacy",
                          income:
                            financialSummary.data.income_breakdown
                              ?.legacy_payments || 0,
                          expense:
                            financialSummary.data.expense_breakdown
                              ?.legacy_expenses || 0,
                        },
                        {
                          category: "Hourly",
                          income:
                            financialSummary.data.income_breakdown
                              ?.hourly_income || 0,
                          expense:
                            financialSummary.data.expense_breakdown
                              ?.hourly_expenses || 0,
                        },
                        {
                          category: "Project",
                          income:
                            financialSummary.data.income_breakdown
                              ?.project_income || 0,
                          expense:
                            financialSummary.data.expense_breakdown
                              ?.project_expenses || 0,
                        },
                      ]}
                      margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="category" stroke="#6b7280" />
                      <YAxis stroke="#6b7280" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#fff",
                          border: "1px solid #e5e7eb",
                          borderRadius: "8px",
                        }}
                        formatter={(value) => `$${value.toFixed(2)}`}
                      />
                      <Legend />
                      <Bar
                        dataKey="income"
                        fill="#10b981"
                        radius={[8, 8, 0, 0]}
                      />
                      <Bar
                        dataKey="expense"
                        fill="#f59e0b"
                        radius={[8, 8, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Profit Trend Chart */}
            {profitTrend && (
              <div className="card-lg">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  30-Day Profit Trend
                </h2>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={(profitTrend.data?.data || [])
                        .slice(-30)
                        .map((day) => ({
                          date: new Date(day.date).toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                          }),
                          profit: day.profit || 0,
                        }))}
                      margin={{ top: 5, right: 30, left: 0, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="date" stroke="#6b7280" />
                      <YAxis stroke="#6b7280" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#fff",
                          border: "1px solid #e5e7eb",
                          borderRadius: "8px",
                        }}
                        formatter={(value) => `$${value.toFixed(2)}`}
                      />
                      <Line
                        type="monotone"
                        dataKey="profit"
                        stroke="#0ea5e9"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>

          {/* Top Projects */}
          {topProjects && (
            <div className="card-lg">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">
                Top Projects by Revenue
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Pie Chart */}
                <div className="flex items-center justify-center">
                  <div className="w-full h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={(topProjects.data?.data || [])
                            .slice(0, 5)
                            .map((p) => ({
                              name: p.project_name,
                              value: p.income || 0,
                            }))}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, value }) =>
                            `${name}: $${value.toFixed(0)}`
                          }
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {(topProjects.data?.data || [])
                            .slice(0, 5)
                            .map((_, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={COLORS[index]}
                              />
                            ))}
                        </Pie>
                        <Tooltip
                          formatter={(value) => `$${value.toFixed(2)}`}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Project Details */}
                <div className="space-y-4">
                  {(topProjects.data?.data || [])
                    .slice(0, 5)
                    .map((project, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: COLORS[idx] }}
                          />
                          <div>
                            <p className="font-medium text-gray-900">
                              {project.project_name}
                            </p>
                            <p className="text-sm text-gray-600">
                              Profit: ${(project.profit || 0).toFixed(2)}
                            </p>
                          </div>
                        </div>
                        <p className="font-semibold text-gray-900">
                          ${(project.income || 0).toFixed(2)}
                        </p>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
