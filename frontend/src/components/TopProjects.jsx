import { Award } from "lucide-react";

export default function TopProjects({ data }) {
  // data = axios response: {success, data: {data: [...ProjectStatsOut], meta: {}}}
  const projects = data?.data?.data || [];
  if (projects.length === 0) {
    return (
      <div className="card-lg">
        <p className="text-gray-600">No project data available</p>
      </div>
    );
  }

  const maxProfit = Math.max(...projects.map((p) => p.profit || 0)) || 1;

  return (
    <div className="card-lg">
      <div className="flex items-center gap-3 mb-6">
        <Award className="text-primary-600" size={24} />
        <h2 className="text-xl font-bold text-gray-900">Top Projects</h2>
      </div>

      <div className="space-y-4">
        {projects.slice(0, 5).map((project, idx) => (
          <div
            key={idx}
            className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900 text-sm">
                {idx + 1}. {project.project_name}
              </h3>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Income</span>
                <span className="font-medium text-green-600">
                  ${(project.income || 0).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Expenses</span>
                <span className="font-medium text-orange-600">
                  ${(project.expense || 0).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between pt-2 border-t border-gray-200">
                <span className="text-gray-600">Profit</span>
                <span
                  className={`font-bold ${
                    (project.profit || 0) >= 0
                      ? "text-green-600"
                      : "text-red-600"
                  }`}
                >
                  ${(project.profit || 0).toFixed(2)}
                </span>
              </div>
            </div>

            {/* Progress bar */}
            <div className="mt-3">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all"
                  style={{
                    width: `${Math.min(100, ((project.profit || 0) / maxProfit) * 100)}%`,
                  }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      {data.projects.length > 5 && (
        <p className="text-sm text-gray-500 mt-4 text-center">
          +{data.projects.length - 5} more projects
        </p>
      )}
    </div>
  );
}
