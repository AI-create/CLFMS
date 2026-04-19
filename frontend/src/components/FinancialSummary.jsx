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
  if (!data?.daily_breakdown) {
    return null;
  }

  // Transform data for chart
  const chartData = data.daily_breakdown.slice(-7).map((day) => ({
    date: new Date(day.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
    income: day.income || 0,
    expenses: day.expenses || 0,
  }));

  return (
    <div className="card-lg">
      <div className="flex items-center gap-3 mb-6">
        <DollarSign className="text-primary-600" size={24} />
        <h2 className="text-xl font-bold text-gray-900">Financial Summary</h2>
      </div>

      {/* Summary metrics */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Total Income</p>
          <p className="text-2xl font-bold text-blue-600">
            ${(data.total_income || 0).toFixed(2)}
          </p>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600 mb-1">Total Expenses</p>
          <p className="text-2xl font-bold text-orange-600">
            ${(data.total_expenses || 0).toFixed(2)}
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
            <Legend />
            <Bar dataKey="income" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            <Bar dataKey="expenses" fill="#f59e0b" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Breakdown items */}
      <div className="mt-6 space-y-3">
        {data.income_breakdown && data.income_breakdown.length > 0 && (
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Income Sources</h3>
            <div className="space-y-2">
              {data.income_breakdown.map((item, idx) => (
                <div
                  key={idx}
                  className="flex justify-between items-center text-sm"
                >
                  <span className="text-gray-600">{item.type || "Other"}</span>
                  <span className="font-medium text-gray-900">
                    ${(item.amount || 0).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
