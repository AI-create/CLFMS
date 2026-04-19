import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";
import { TrendingUp } from "lucide-react";

export default function ProfitTrend({ data }) {
  if (!data?.trends || data.trends.length === 0) {
    return (
      <div className="card-lg">
        <p className="text-gray-600">No profit trend data available</p>
      </div>
    );
  }

  // Transform data for chart
  const chartData = data.trends.slice(-30).map((day) => ({
    date: new Date(day.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
    profit: day.profit || 0,
    income: day.income || 0,
    expenses: day.expenses || 0,
  }));

  const avgProfit =
    chartData.reduce((sum, d) => sum + d.profit, 0) / chartData.length;
  const maxProfit = Math.max(...chartData.map((d) => d.profit));
  const minProfit = Math.min(...chartData.map((d) => d.profit));

  return (
    <div className="card-lg">
      <div className="flex items-center gap-3 mb-6">
        <TrendingUp className="text-primary-600" size={24} />
        <h2 className="text-xl font-bold text-gray-900">30-Day Profit Trend</h2>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-xs text-gray-600">Average Daily</p>
          <p className="text-lg font-bold text-gray-900">
            ${avgProfit.toFixed(2)}
          </p>
        </div>
        <div className="bg-green-50 p-3 rounded-lg">
          <p className="text-xs text-gray-600">Best Day</p>
          <p className="text-lg font-bold text-green-600">
            ${maxProfit.toFixed(2)}
          </p>
        </div>
        <div className="bg-red-50 p-3 rounded-lg">
          <p className="text-xs text-gray-600">Worst Day</p>
          <p className="text-lg font-bold text-red-600">
            ${Math.abs(minProfit).toFixed(2)}
          </p>
        </div>
      </div>

      {/* Chart */}
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              style={{ fontSize: "12px" }}
            />
            <YAxis stroke="#6b7280" style={{ fontSize: "12px" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #e5e7eb",
                borderRadius: "8px",
              }}
              formatter={(value) => [
                value >= 0
                  ? `+$${value.toFixed(2)}`
                  : `-$${Math.abs(value).toFixed(2)}`,
                "Profit",
              ]}
              labelFormatter={(date) => `Date: ${date}`}
            />
            <Area
              type="monotone"
              dataKey="profit"
              stroke="#0ea5e9"
              fillOpacity={1}
              fill="url(#colorProfit)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
