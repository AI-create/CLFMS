import { TrendingUp, TrendingDown, Target, AlertCircle } from "lucide-react";

const iconMap = {
  TrendingUp: TrendingUp,
  TrendingDown: TrendingDown,
  Target: Target,
  AlertCircle: AlertCircle,
};

export default function KPICard({ title, value, change, icon }) {
  const Icon = iconMap[icon];
  const isPositive = change >= 0;
  const changeColor = isPositive ? "text-green-600" : "text-red-600";
  const changeBgColor = isPositive ? "bg-green-50" : "bg-red-50";

  return (
    <div className="card-lg">
      <div className="flex items-center justify-between mb-4">
        <h3 className="metric-label">{title}</h3>
        {Icon && <Icon className="text-gray-400" size={20} />}
      </div>
      <div className="space-y-2">
        <p className="metric-value">{value}</p>
        {change !== undefined && (
          <p className={`text-sm font-medium ${changeColor}`}>
            {isPositive ? "↑" : "↓"} {Math.abs(change).toFixed(1)}% this month
          </p>
        )}
      </div>
    </div>
  );
}
