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
  ChevronDown,
  ChevronUp,
  FlaskConical,
  BookOpen,
} from "lucide-react";

const API_URL = "/api/v1";

const EMPTY_PROJECT_FORM = {
  name: "",
  description: "",
  research_type: "internal_rnd",
  objectives: "",
  status: "planned",
};

const EMPTY_EXP_FORM = {
  title: "",
  description: "",
  objective: "",
  hypothesis: "",
  status: "planned",
  conducted_by: "",
};

const EMPTY_LOG_FORM = {
  title: "",
  notes: "",
  observations: "",
  recorded_by: "",
};

export default function ResearchPage() {
  const [research, setResearch] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  // Project form
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState(EMPTY_PROJECT_FORM);

  // Expand state
  const [expandedProject, setExpandedProject] = useState(null);

  // Experiment form
  const [showExpForm, setShowExpForm] = useState(false);
  const [expProjectId, setExpProjectId] = useState(null);
  const [expForm, setExpForm] = useState(EMPTY_EXP_FORM);
  const [expSubmitting, setExpSubmitting] = useState(false);

  // Log form
  const [showLogForm, setShowLogForm] = useState(false);
  const [logExpId, setLogExpId] = useState(null);
  const [logProjectId, setLogProjectId] = useState(null);
  const [logForm, setLogForm] = useState(EMPTY_LOG_FORM);
  const [logSubmitting, setLogSubmitting] = useState(false);

  useEffect(() => {
    fetchResearch();
  }, []);

  const fetchResearch = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/research-projects`);
      setResearch(response.data.data?.data || []);
      setError(null);
    } catch (err) {
      console.error("Error fetching research:", err);
      setError(apiError(err, "Failed to load research data"));
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingItem) {
        await axios.put(
          `${API_URL}/research-projects/${editingItem.id}`,
          formData,
        );
      } else {
        await axios.post(`${API_URL}/research-projects`, formData);
      }
      setShowForm(false);
      setFormData(EMPTY_PROJECT_FORM);
      setEditingItem(null);
      fetchResearch();
    } catch (err) {
      setError(apiError(err, "Failed to save research"));
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this research?"))
      return;

    try {
      await axios.delete(`${API_URL}/research-projects/${id}`);
      setResearch(research.filter((r) => r.id !== id));
    } catch (err) {
      setError(apiError(err, "Failed to delete research"));
    }
  };

  const handleAddExperiment = async (e) => {
    e.preventDefault();
    setExpSubmitting(true);
    try {
      const payload = { ...expForm };
      if (!payload.conducted_by) delete payload.conducted_by;
      await axios.post(
        `${API_URL}/research-projects/${expProjectId}/experiments`,
        payload,
      );
      setShowExpForm(false);
      setExpForm(EMPTY_EXP_FORM);
      fetchResearch();
    } catch (err) {
      alert(apiError(err, "Failed to add experiment"));
    } finally {
      setExpSubmitting(false);
    }
  };

  const handleAddLog = async (e) => {
    e.preventDefault();
    setLogSubmitting(true);
    try {
      const payload = { ...logForm };
      if (!payload.title) delete payload.title;
      if (!payload.observations) delete payload.observations;
      if (!payload.recorded_by) delete payload.recorded_by;
      await axios.post(`${API_URL}/experiments/${logExpId}/logs`, payload);
      setShowLogForm(false);
      setLogForm(EMPTY_LOG_FORM);
      // Refresh the specific project
      const res = await axios.get(
        `${API_URL}/research-projects/${logProjectId}`,
      );
      setResearch((prev) =>
        prev.map((r) => (r.id === logProjectId ? res.data.data : r)),
      );
    } catch (err) {
      alert(apiError(err, "Failed to add log"));
    } finally {
      setLogSubmitting(false);
    }
  };

  const filteredResearch = research.filter(
    (item) =>
      !searchTerm ||
      item.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.description?.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Research Projects</h1>
        <button
          onClick={() => {
            setEditingItem(null);
            setFormData(EMPTY_PROJECT_FORM);
            setShowForm(true);
          }}
          className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          <Plus size={20} />
          New Research
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Project Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg shadow-lg max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingItem ? "Edit Research" : "New Research Project"}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                type="text"
                placeholder="Project Name *"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
              <select
                value={formData.research_type}
                onChange={(e) =>
                  setFormData({ ...formData, research_type: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="internal_rnd">Internal R&D</option>
                <option value="client_research">Client Research</option>
                <option value="market_research">Market Research</option>
                <option value="feasibility">Feasibility Study</option>
              </select>
              <textarea
                placeholder="Description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-20"
              />
              <textarea
                placeholder="Objectives"
                value={formData.objectives}
                onChange={(e) =>
                  setFormData({ ...formData, objectives: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-20"
              />
              <select
                value={formData.status}
                onChange={(e) =>
                  setFormData({ ...formData, status: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="planned">Planned</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="on_hold">On Hold</option>
              </select>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Experiment Form Modal */}
      {showExpForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg shadow-lg max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Add Experiment</h2>
            <form onSubmit={handleAddExperiment} className="space-y-4">
              <input
                type="text"
                placeholder="Experiment Title *"
                value={expForm.title}
                onChange={(e) =>
                  setExpForm({ ...expForm, title: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
              <textarea
                placeholder="Description"
                value={expForm.description}
                onChange={(e) =>
                  setExpForm({ ...expForm, description: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-16"
              />
              <textarea
                placeholder="Objective"
                value={expForm.objective}
                onChange={(e) =>
                  setExpForm({ ...expForm, objective: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-16"
              />
              <input
                type="text"
                placeholder="Hypothesis"
                value={expForm.hypothesis}
                onChange={(e) =>
                  setExpForm({ ...expForm, hypothesis: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <div className="grid grid-cols-2 gap-4">
                <select
                  value={expForm.status}
                  onChange={(e) =>
                    setExpForm({ ...expForm, status: e.target.value })
                  }
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="planned">Planned</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="failed">Failed</option>
                </select>
                <input
                  type="text"
                  placeholder="Conducted By"
                  value={expForm.conducted_by}
                  onChange={(e) =>
                    setExpForm({ ...expForm, conducted_by: e.target.value })
                  }
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowExpForm(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={expSubmitting}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {expSubmitting ? "Adding..." : "Add Experiment"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Research Log Form Modal */}
      {showLogForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg shadow-lg max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Add Research Log</h2>
            <form onSubmit={handleAddLog} className="space-y-4">
              <input
                type="text"
                placeholder="Log Title (optional)"
                value={logForm.title}
                onChange={(e) =>
                  setLogForm({ ...logForm, title: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <textarea
                placeholder="Notes *"
                value={logForm.notes}
                onChange={(e) =>
                  setLogForm({ ...logForm, notes: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-24"
                required
              />
              <textarea
                placeholder="Observations"
                value={logForm.observations}
                onChange={(e) =>
                  setLogForm({ ...logForm, observations: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-16"
              />
              <input
                type="text"
                placeholder="Recorded By"
                value={logForm.recorded_by}
                onChange={(e) =>
                  setLogForm({ ...logForm, recorded_by: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowLogForm(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={logSubmitting}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {logSubmitting ? "Adding..." : "Add Log"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-3 text-gray-400" size={20} />
        <input
          type="text"
          placeholder="Search research..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      ) : filteredResearch.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg">
          <p className="text-gray-500">No research projects found</p>
        </div>
      ) : (
        /* Research List */
        <div className="grid gap-4">
          {filteredResearch.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-lg shadow border border-gray-200 hover:shadow-md transition"
            >
              {/* Project Header */}
              <div className="p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {item.name}
                      </h3>
                      <span
                        className={`px-2 py-1 rounded text-sm font-medium ${
                          item.status === "completed"
                            ? "bg-green-100 text-green-800"
                            : item.status === "active"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-yellow-100 text-yellow-800"
                        }`}
                      >
                        {item.status}
                      </span>
                    </div>
                    {item.research_type && (
                      <p className="text-sm text-gray-600 mb-2">
                        Type: {item.research_type.replace(/_/g, " ")}
                      </p>
                    )}
                    {item.description && (
                      <p className="text-gray-700 mb-2">{item.description}</p>
                    )}
                    {item.objectives && (
                      <div className="mt-3 p-3 bg-blue-50 rounded">
                        <p className="text-sm font-medium text-gray-900">
                          Objectives:
                        </p>
                        <p className="text-sm text-gray-700 mt-1">
                          {item.objectives}
                        </p>
                      </div>
                    )}
                    <div className="flex gap-4 mt-3 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <FlaskConical size={14} />
                        {item.experiments?.length || 0} experiments
                      </span>
                      <span className="flex items-center gap-1">
                        <BookOpen size={14} />
                        {item.logs?.length || 0} logs
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() =>
                        setExpandedProject(
                          expandedProject === item.id ? null : item.id,
                        )
                      }
                      className="p-2 text-gray-500 hover:bg-gray-100 rounded"
                      title="Show experiments"
                    >
                      {expandedProject === item.id ? (
                        <ChevronUp size={20} />
                      ) : (
                        <ChevronDown size={20} />
                      )}
                    </button>
                    <button
                      onClick={() => {
                        setEditingItem(item);
                        setFormData({
                          name: item.name,
                          description: item.description || "",
                          research_type: item.research_type || "internal_rnd",
                          objectives: item.objectives || "",
                          status: item.status || "planned",
                        });
                        setShowForm(true);
                      }}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                    >
                      <Edit size={20} />
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded"
                    >
                      <Trash2 size={20} />
                    </button>
                  </div>
                </div>
              </div>

              {/* Experiments Panel */}
              {expandedProject === item.id && (
                <div className="border-t border-gray-200 p-6 bg-gray-50">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-semibold text-gray-800 flex items-center gap-2">
                      <FlaskConical size={16} />
                      Experiments
                    </h4>
                    <button
                      onClick={() => {
                        setExpProjectId(item.id);
                        setExpForm(EMPTY_EXP_FORM);
                        setShowExpForm(true);
                      }}
                      className="flex items-center gap-1 px-3 py-1 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                    >
                      <Plus size={14} />
                      Add Experiment
                    </button>
                  </div>

                  {!item.experiments || item.experiments.length === 0 ? (
                    <p className="text-gray-400 text-sm">
                      No experiments yet. Add the first one.
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {item.experiments.map((exp) => (
                        <div
                          key={exp.id}
                          className="bg-white border border-gray-200 rounded-lg p-4"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <h5 className="font-medium text-gray-900">
                                {exp.title}
                              </h5>
                              <span
                                className={`px-2 py-0.5 rounded text-xs ${
                                  exp.status === "completed"
                                    ? "bg-green-100 text-green-800"
                                    : exp.status === "active"
                                      ? "bg-blue-100 text-blue-800"
                                      : exp.status === "failed"
                                        ? "bg-red-100 text-red-800"
                                        : "bg-yellow-100 text-yellow-800"
                                }`}
                              >
                                {exp.status}
                              </span>
                              {exp.has_ip_potential && (
                                <span className="px-2 py-0.5 rounded text-xs bg-purple-100 text-purple-800">
                                  IP Potential
                                </span>
                              )}
                              {exp.is_reproducible && (
                                <span className="px-2 py-0.5 rounded text-xs bg-teal-100 text-teal-800">
                                  Reproducible
                                </span>
                              )}
                            </div>
                            <button
                              onClick={() => {
                                setLogExpId(exp.id);
                                setLogProjectId(item.id);
                                setLogForm(EMPTY_LOG_FORM);
                                setShowLogForm(true);
                              }}
                              className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded"
                            >
                              <Plus size={12} />
                              Add Log
                            </button>
                          </div>
                          {exp.description && (
                            <p className="text-sm text-gray-600 mb-1">
                              {exp.description}
                            </p>
                          )}
                          {exp.hypothesis && (
                            <p className="text-sm text-gray-500 italic">
                              Hypothesis: {exp.hypothesis}
                            </p>
                          )}
                          {exp.conducted_by && (
                            <p className="text-xs text-gray-400 mt-1">
                              By: {exp.conducted_by}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Research Logs */}
                  {item.logs && item.logs.length > 0 && (
                    <div className="mt-4">
                      <h4 className="font-semibold text-gray-800 flex items-center gap-2 mb-3">
                        <BookOpen size={16} />
                        Research Logs ({item.logs.length})
                      </h4>
                      <div className="space-y-2">
                        {item.logs.map((log) => (
                          <div
                            key={log.id}
                            className="bg-white border border-gray-200 rounded p-3"
                          >
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm font-medium text-gray-800">
                                {log.title || `Log #${log.version}`}
                              </span>
                              <span className="text-xs text-gray-400">
                                {new Date(log.recorded_at).toLocaleDateString()}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600">{log.notes}</p>
                            {log.observations && (
                              <p className="text-xs text-gray-500 mt-1 italic">
                                {log.observations}
                              </p>
                            )}
                            {log.recorded_by && (
                              <p className="text-xs text-gray-400 mt-1">
                                By: {log.recorded_by}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
