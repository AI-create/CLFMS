import { useState, useEffect } from "react";
import { apiError } from "../utils/apiError";
import axios from "axios";
import KPICard from "../components/KPICard";
import FinancialSummary from "../components/FinancialSummary";
import ProfitTrend from "../components/ProfitTrend";
import TopProjects from "../components/TopProjects";
import { AlertCircle, Loader } from "lucide-react";

const API_URL = "/api/v1";

export default function Dashboard() {
  const [kpis, setKpis] = useState(null);
  const [financialSummary, setFinancialSummary] = useState(null);
  const [profitTrend, setProfitTrend] = useState(null);
  const [topProjects, setTopProjects] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [kpiRes, finRes, trendRes, projRes] = await Promise.all([
          axios.get(`${API_URL}/dashboard/kpis`),
          axios.get(`${API_URL}/dashboard/financial-summary`),
          axios.get(`${API_URL}/dashboard/profit-trend`),
          axios.get(`${API_URL}/dashboard/top-projects`),
        ]);

        setKpis(kpiRes.data);
        setFinancialSummary(finRes.data);
        setProfitTrend(trendRes.data);
        setTopProjects(projRes.data);
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
        setError(apiError(err, "Failed to load dashboard data"));
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();

    // Refresh data every 5 minutes
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center h-96">
          <div className="flex flex-col items-center gap-3">
            <Loader className="animate-spin text-primary-600" size={32} />
            <p className="text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      ) : (
        <>
          {/* KPI Cards */}
          {kpis && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <KPICard
                title="Total Revenue"
                value={`$${(kpis.data?.revenue || 0).toFixed(2)}`}
                icon="TrendingUp"
              />
              <KPICard
                title="Net Profit"
                value={`$${(kpis.data?.profit || 0).toFixed(2)}`}
                icon="Target"
              />
              <KPICard
                title="Pending Payments"
                value={`$${(kpis.data?.pending_payments || 0).toFixed(2)}`}
                icon="AlertCircle"
              />
              <KPICard
                title="Active Projects"
                value={kpis.data?.active_projects || 0}
                icon="Briefcase"
              />
            </div>
          )}

          {/* Main content grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left column - Financial summary and trend */}
            <div className="lg:col-span-2 space-y-8">
              {financialSummary && <FinancialSummary data={financialSummary} />}
              {profitTrend && <ProfitTrend data={profitTrend} />}
            </div>

            {/* Right column - Top projects */}
            <div>{topProjects && <TopProjects data={topProjects} />}</div>
          </div>
        </>
      )}
    </div>
  );
}
