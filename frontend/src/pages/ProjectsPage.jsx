import { useState, useEffect } from "react";
import { apiError } from "../utils/apiError";
import axios from "axios";
import {
  Plus,
  Edit,
  Trash2,
  AlertCircle,
  Loader,
  Search,
  TrendingUp,
  ChevronDown,
  ChevronUp,
  Lock,
} from "lucide-react";
import ProjectForm from "../components/ProjectForm";
import { useProjectLocks } from "../hooks/useProjectLocks";

const API_URL = "/api/v1";

export default function ProjectsPage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [showForm, setShowForm] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [expandedFinance, setExpandedFinance] = useState(null);
  const [financeSummary, setFinanceSummary] = useState({});
  const { getProjectLock } = useProjectLocks();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/projects`);
      setProjects(response.data.data?.data || []);
      setError(null);
    } catch (err) {
      console.error("Error fetching projects:", err);
      setError(apiError(err, "Failed to load projects"));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (projectId) => {
    if (!window.confirm("Are you sure you want to delete this project?"))
      return;

    try {
      await axios.delete(`${API_URL}/projects/${projectId}`);
      setProjects(projects.filter((p) => p.id !== projectId));
    } catch (err) {
      setError(apiError(err, "Failed to delete project"));
    }
  };

  const handleToggleFinance = async (projectId) => {
    if (expandedFinance === projectId) {
      setExpandedFinance(null);
    } else {
      setExpandedFinance(projectId);
      if (!financeSummary[projectId]) {
        try {
          const res = await axios.get(
            `${API_URL}/finance/project/${projectId}`,
          );
          setFinanceSummary((prev) => ({
            ...prev,
            [projectId]: res.data.data,
          }));
        } catch (err) {
          setFinanceSummary((prev) => ({ ...prev, [projectId]: null }));
        }
      }
    }
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingProject(null);
  };

  const handleFormSubmit = async () => {
    await fetchProjects();
    handleFormClose();
  };

  const filteredProjects = projects.filter((project) => {
    const matchesSearch = project.name
      ?.toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesStatus =
      statusFilter === "all" || project.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const statuses = ["all", "active", "pending", "completed", "on_hold"];
  const statusColors = {
    active: "bg-green-100 text-green-800",
    pending: "bg-yellow-100 text-yellow-800",
    completed: "bg-blue-100 text-blue-800",
    on_hold: "bg-gray-100 text-gray-800",
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
        <button
          onClick={() => setShowForm(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          New Project
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-3 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search projects..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
        >
          {statuses.map((status) => (
            <option key={status} value={status}>
              {status === "all"
                ? "All Statuses"
                : status.charAt(0).toUpperCase() +
                  status.slice(1).replace("_", " ")}
            </option>
          ))}
        </select>
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <p className="text-gray-500 text-lg">
                {searchTerm || statusFilter !== "all"
                  ? "No projects match your filters"
                  : "No projects found"}
              </p>
            </div>
          ) : (
            filteredProjects.map((project) => (
              <div
                key={project.id}
                className="card-lg hover:shadow-md transition"
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 flex-1">
                    {project.name}
                  </h3>
                  <span
                    className={`text-xs font-medium px-2 py-1 rounded ${statusColors[project.status] || "bg-gray-100"}`}
                  >
                    {project.status?.charAt(0).toUpperCase() +
                      project.status?.slice(1)}
                  </span>
                </div>

                {project.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {project.description}
                  </p>
                )}

                <div className="space-y-2 mb-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Budget</span>
                    <span className="font-medium text-gray-900">
                      ${(project.budget || 0).toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Start Date</span>
                    <span className="font-medium text-gray-900">
                      {project.start_date
                        ? new Date(project.start_date).toLocaleDateString()
                        : "-"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">End Date</span>
                    <span className="font-medium text-gray-900">
                      {project.end_date
                        ? new Date(project.end_date).toLocaleDateString()
                        : "-"}
                    </span>
                  </div>
                </div>

                <div className="flex gap-2 pt-4 border-t border-gray-200">
                  {(() => {
                    const lock = getProjectLock(project.id);
                    return (
                      <>
                        <button
                          onClick={() => handleToggleFinance(project.id)}
                          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm text-purple-600 hover:bg-purple-50 rounded transition"
                        >
                          <TrendingUp size={16} />
                          Finances
                          {expandedFinance === project.id ? (
                            <ChevronUp size={14} />
                          ) : (
                            <ChevronDown size={14} />
                          )}
                        </button>
                        <button
                          onClick={() => {
                            if (!lock.can_edit) return;
                            setEditingProject(project);
                            setShowForm(true);
                          }}
                          disabled={!lock.can_edit}
                          title={
                            !lock.can_edit
                              ? `Project is ${lock.status} — editing disabled`
                              : undefined
                          }
                          className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm rounded transition ${
                            lock.can_edit
                              ? "text-blue-600 hover:bg-blue-50"
                              : "text-gray-400 cursor-not-allowed bg-gray-50"
                          }`}
                        >
                          {lock.locked && !lock.can_edit ? (
                            <Lock size={14} />
                          ) : (
                            <Edit size={16} />
                          )}
                          Edit
                        </button>
                        <button
                          onClick={() => {
                            if (!lock.can_delete) return;
                            handleDelete(project.id);
                          }}
                          disabled={!lock.can_delete}
                          title={
                            !lock.can_delete
                              ? `Project is ${lock.status} — deletion disabled`
                              : undefined
                          }
                          className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm rounded transition ${
                            lock.can_delete
                              ? "text-red-600 hover:bg-red-50"
                              : "text-gray-400 cursor-not-allowed bg-gray-50"
                          }`}
                        >
                          {lock.locked && !lock.can_delete ? (
                            <Lock size={14} />
                          ) : (
                            <Trash2 size={16} />
                          )}
                          Delete
                        </button>
                      </>
                    );
                  })()}
                </div>
                {expandedFinance === project.id && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    {financeSummary[project.id] === undefined ? (
                      <Loader
                        className="animate-spin text-primary-600 mx-auto"
                        size={18}
                      />
                    ) : financeSummary[project.id] === null ? (
                      <p className="text-xs text-gray-400 text-center">
                        No financial data available
                      </p>
                    ) : (
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div className="bg-green-50 rounded p-2">
                          <p className="text-xs text-gray-500">Revenue</p>
                          <p className="font-semibold text-green-700">
                            $
                            {(financeSummary[project.id].revenue || 0).toFixed(
                              2,
                            )}
                          </p>
                        </div>
                        <div className="bg-red-50 rounded p-2">
                          <p className="text-xs text-gray-500">Cost</p>
                          <p className="font-semibold text-red-700">
                            ${(financeSummary[project.id].cost || 0).toFixed(2)}
                          </p>
                        </div>
                        <div className="bg-blue-50 rounded p-2">
                          <p className="text-xs text-gray-500">Profit</p>
                          <p className="font-semibold text-blue-700">
                            $
                            {(financeSummary[project.id].profit || 0).toFixed(
                              2,
                            )}
                          </p>
                        </div>
                        <div className="bg-purple-50 rounded p-2">
                          <p className="text-xs text-gray-500">Margin</p>
                          <p className="font-semibold text-purple-700">
                            {(financeSummary[project.id].margin || 0).toFixed(
                              1,
                            )}
                            %
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Form Modal */}
      {showForm && (
        <ProjectForm
          project={editingProject}
          onClose={handleFormClose}
          onSubmit={handleFormSubmit}
        />
      )}
    </div>
  );
}
