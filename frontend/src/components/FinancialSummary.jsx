import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { DollarSign } from "lucide-react";

export default function FinancialSummary({ data }) {
  // data = axios response: {success, data: {total_income, total_expense, income_breakdown, expense_breakdown}}
  const summary = data?.data;
  if (!summary) return null;

  const incBreakdown = summary.income_breakdown || {};
  const expBreakdown = summary.expense_breakdown || {};

  const chartData = [
    {
      name: "Legacy",
      income: incBreakdown.legacy_payments || 0,
      expenses: expBreakdown.legacy_expenses || 0,
    },
    {
      name: "Hourly",
      income: incBreakdown.hourly_income || 0,
      expenses: expBreakdown.hourly_expenses || 0,
    },
    {
      name: "Project",
      income: incBreakdown.project_income || 0,
      expenses: expBreakdown.project_expenses || 0,
    },
  ];

  return (
    <div className="card-lg">
      <div className="flex items-center gap-3 mb-6">
        <DollarSign className="text-primary-600" size={24} />
        <h2 className="text-xl font-bold text-gray-900">Financial Summary</h2>
      </div>

      {/* Summary metrics */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Total Income</p>
          <p className="text-2xl font-bold text-blue-600">
            ${(summary.total_income || 0).toFixed(2)}
          </p>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Total Expenses</p>
          <p className="text-2xl font-bold text-orange-600">
            ${(summary.total_expense || 0).toFixed(2)}
          </p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Net Profit</p>
          <p
            className={`text-2xl font-bold ${(summary.total_profit || 0) >= 0 ? "text-green-600" : "text-red-600"}`}
          >
            ${(summary.total_profit || 0).toFixed(2)}
          </p>
        </div>
      </div>

      {/* Chart */}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="name" stroke="#6b7280" />
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
              fill="#3b82f6"
              radius={[8, 8, 0, 0]}
              name="Income"
            />
            <Bar
              dataKey="expenses"
              fill="#f59e0b"
              radius={[8, 8, 0, 0]}
              name="Expenses"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
