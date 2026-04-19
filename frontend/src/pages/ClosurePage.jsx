import { useState, useEffect } from "react";
import axios from "axios";
import {
  Plus,
  Edit,
  AlertCircle,
  Loader,
  Search,
  Archive,
  CheckCircle,
  Clock,
  XCircle,
} from "lucide-react";

const API_URL = "/api/v1";

export default function ClosurePage() {
  const [closures, setClosures] = useState([]); // [{...projectClosureResponse, project_name}]
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  // Initiate form
  const [showInitForm, setShowInitForm] = useState(false);
  const [initProjectId, setInitProjectId] = useState("");
  const [initFormData, setInitFormData] = useState({
    deliverables_description: "",
    closure_notes: "",
  });
  const [initiating, setInitiating] = useState(false);

  // Edit form
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingClosure, setEditingClosure] = useState(null);
  const [editFormData, setEditFormData] = useState({
    closure_notes: "",
    client_feedback: "",
    client_satisfaction_rating: "",
    deliverables_description: "",
  });

  useEffect(() => {
    fetchAll();
  }, []);

  const fetchAll = async () => {
    try {
      setLoading(true);
      const projRes = await axios.get(`${API_URL}/projects`);
      const allProjects = projRes.data.data?.data || [];
      setProjects(allProjects);

      // Fetch closure status for each project in parallel
      const results = await Promise.allSettled(
        allProjects.map((p) =>
          axios
            .get(`${API_URL}/closure/projects/${p.id}`)
            .then((r) => ({ ...r.data.data, project_name: p.name || p.title })),
        ),
      );

      const closureData = results
        .filter((r) => r.status === "fulfilled" && r.value?.id)
        .map((r) => r.value);

      setClosures(closureData);
      setError(null);
    } catch (err) {
      console.error("Error fetching closures:", err);
      setError(err.response?.data?.detail || "Failed to load closure data");
    } finally {
      setLoading(false);
    }
  };

  const handleInitiateClosure = async (e) => {
    e.preventDefault();
    if (!initProjectId) return;
    setInitiating(true);
    try {
      await axios.post(
        `${API_URL}/closure/projects/${initProjectId}/initiate`,
        initFormData,
      );
      setShowInitForm(false);
      setInitProjectId("");
      setInitFormData({ deliverables_description: "", closure_notes: "" });
      fetchAll();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to initiate closure");
    } finally {
      setInitiating(false);
    }
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = { ...editFormData };
      if (payload.client_satisfaction_rating === "") {
        delete payload.client_satisfaction_rating;
      } else {
        payload.client_satisfaction_rating = parseInt(
          payload.client_satisfaction_rating,
        );
      }
      await axios.put(
        `${API_URL}/closure/projects/${editingClosure.project_id}`,
        payload,
      );
      setShowEditForm(false);
      fetchAll();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update closure");
    }
  };

  const handleMarkDeliverablesComplete = async (projectId) => {
    try {
      await axios.post(
        `${API_URL}/closure/projects/${projectId}/mark-deliverables-complete`,
        {},
      );
      fetchAll();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to mark deliverables complete",
      );
    }
  };

  const handleMarkPaymentReceived = async (projectId) => {
    const amount = window.prompt("Enter final payment amount:");
    if (!amount) return;
    try {
      await axios.post(
        `${API_URL}/closure/projects/${projectId}/mark-payment-received`,
        { amount: parseFloat(amount) },
      );
      fetchAll();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to mark payment received");
    }
  };

  const handleMarkCompleted = async (projectId) => {
    if (!window.confirm("Mark this project closure as completed?")) return;
    try {
      await axios.post(
        `${API_URL}/closure/projects/${projectId}/mark-completed`,
        {},
      );
      fetchAll();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to mark closure completed",
      );
    }
  };

  const handleArchive = async (projectId) => {
    const reason = window.prompt("Reason for archiving (optional):");
    try {
      await axios.post(`${API_URL}/closure/projects/${projectId}/archive`, {
        reason: reason || "",
      });
      fetchAll();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to archive closure");
    }
  };

  const statusBadge = (status) => {
    const map = {
      in_progress: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      on_hold: "bg-yellow-100 text-yellow-800",
      archived: "bg-gray-100 text-gray-800",
    };
    return map[status] || "bg-gray-100 text-gray-700";
  };

  // Projects that don't already have a closure
  const initiatedProjectIds = new Set(closures.map((c) => c.project_id));
  const availableProjects = projects.filter(
    (p) => !initiatedProjectIds.has(p.id),
  );

  const filteredClosures = closures.filter(
    (c) =>
      !searchTerm ||
      c.project_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.status?.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Project Closure</h1>
          <p className="text-gray-600 mt-1">
            Manage project closure and archival
          </p>
        </div>
        <button
          onClick={() => {
            setInitProjectId("");
            setInitFormData({
              deliverables_description: "",
              closure_notes: "",
            });
            setShowInitForm(true);
          }}
          disabled={availableProjects.length === 0}
          className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50"
        >
          <Plus size={20} />
          Initiate Closure
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-600 hover:text-red-800"
          >
            <XCircle size={18} />
          </button>
        </div>
      )}

      {/* Initiate Closure Modal */}
      {showInitForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg shadow-lg max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              Initiate Project Closure
            </h2>
            <form onSubmit={handleInitiateClosure} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project *
                </label>
                <select
                  value={initProjectId}
                  onChange={(e) => setInitProjectId(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                >
                  <option value="">Select a project</option>
                  {availableProjects.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name || p.title}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Deliverables Description
                </label>
                <textarea
                  value={initFormData.deliverables_description}
                  onChange={(e) =>
                    setInitFormData({
                      ...initFormData,
                      deliverables_description: e.target.value,
                    })
                  }
                  rows={3}
                  placeholder="Describe the deliverables for this project..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Closure Notes
                </label>
                <textarea
                  value={initFormData.closure_notes}
                  onChange={(e) =>
                    setInitFormData({
                      ...initFormData,
                      closure_notes: e.target.value,
                    })
                  }
                  rows={2}
                  placeholder="Any notes about the closure process..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowInitForm(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={initiating}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {initiating ? "Initiating..." : "Initiate Closure"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Closure Modal */}
      {showEditForm && editingClosure && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg shadow-lg max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              Edit Closure — {editingClosure.project_name}
            </h2>
            <form onSubmit={handleEditSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Closure Notes
                </label>
                <textarea
                  value={editFormData.closure_notes}
                  onChange={(e) =>
                    setEditFormData({
                      ...editFormData,
                      closure_notes: e.target.value,
                    })
                  }
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Client Feedback
                </label>
                <textarea
                  value={editFormData.client_feedback}
                  onChange={(e) =>
                    setEditFormData({
                      ...editFormData,
                      client_feedback: e.target.value,
                    })
                  }
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Client Satisfaction (1–5)
                </label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={editFormData.client_satisfaction_rating}
                  onChange={(e) =>
                    setEditFormData({
                      ...editFormData,
                      client_satisfaction_rating: e.target.value,
                    })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowEditForm(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  Save Changes
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
          placeholder="Search closures..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      ) : filteredClosures.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-lg shadow">
          <p className="text-gray-500 text-lg">No closure records found</p>
          <p className="text-gray-400 mt-2 text-sm">
            Use "Initiate Closure" to start the closure process for a completed
            project
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredClosures.map((closure) => (
            <div
              key={closure.id}
              className="bg-white rounded-lg shadow border border-gray-200 p-6"
            >
              {/* Closure Header */}
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {closure.project_name || `Project #${closure.project_id}`}
                  </h3>
                  <p className="text-sm text-gray-500">
                    Initiated:{" "}
                    {new Date(
                      closure.closure_initiated_at,
                    ).toLocaleDateString()}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${statusBadge(closure.status)}`}
                >
                  {closure.status?.replace("_", " ")}
                </span>
              </div>

              {/* Progress Row */}
              <div className="flex flex-wrap gap-6 mb-4 text-sm">
                <div className="flex items-center gap-2">
                  {closure.deliverables_completed ? (
                    <CheckCircle size={16} className="text-green-600" />
                  ) : (
                    <Clock size={16} className="text-yellow-600" />
                  )}
                  <span
                    className={
                      closure.deliverables_completed
                        ? "text-green-700"
                        : "text-gray-600"
                    }
                  >
                    Deliverables
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {closure.final_payment_received ? (
                    <CheckCircle size={16} className="text-green-600" />
                  ) : (
                    <Clock size={16} className="text-yellow-600" />
                  )}
                  <span
                    className={
                      closure.final_payment_received
                        ? "text-green-700"
                        : "text-gray-600"
                    }
                  >
                    Final Payment
                  </span>
                </div>
                {closure.client_satisfaction_rating && (
                  <div className="flex items-center gap-1">
                    <span className="text-yellow-500">
                      {"★".repeat(closure.client_satisfaction_rating)}
                    </span>
                    <span className="text-gray-300">
                      {"★".repeat(5 - closure.client_satisfaction_rating)}
                    </span>
                  </div>
                )}
                {closure.final_profit !== undefined && (
                  <div className="ml-auto">
                    <span className="text-xs text-gray-500">
                      Final Profit:{" "}
                    </span>
                    <span
                      className={`font-semibold ${closure.final_profit >= 0 ? "text-green-600" : "text-red-600"}`}
                    >
                      ${closure.final_profit.toFixed(2)}
                    </span>
                  </div>
                )}
              </div>

              {/* Notes / Feedback */}
              {(closure.closure_notes || closure.client_feedback) && (
                <div className="text-sm text-gray-600 mb-4 space-y-1 bg-gray-50 p-3 rounded">
                  {closure.closure_notes && (
                    <p>
                      <span className="font-medium">Notes:</span>{" "}
                      {closure.closure_notes}
                    </p>
                  )}
                  {closure.client_feedback && (
                    <p>
                      <span className="font-medium">Client Feedback:</span>{" "}
                      {closure.client_feedback}
                    </p>
                  )}
                </div>
              )}

              {/* Actions */}
              {closure.status !== "archived" && (
                <div className="flex flex-wrap gap-2 pt-3 border-t border-gray-100">
                  {!closure.deliverables_completed && (
                    <button
                      onClick={() =>
                        handleMarkDeliverablesComplete(closure.project_id)
                      }
                      className="px-3 py-1.5 text-sm bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100"
                    >
                      ✓ Deliverables Done
                    </button>
                  )}
                  {!closure.final_payment_received && (
                    <button
                      onClick={() =>
                        handleMarkPaymentReceived(closure.project_id)
                      }
                      className="px-3 py-1.5 text-sm bg-green-50 text-green-700 rounded-lg hover:bg-green-100"
                    >
                      $ Payment Received
                    </button>
                  )}
                  {closure.status === "in_progress" &&
                    closure.deliverables_completed &&
                    closure.final_payment_received && (
                      <button
                        onClick={() => handleMarkCompleted(closure.project_id)}
                        className="px-3 py-1.5 text-sm bg-primary-50 text-primary-700 rounded-lg hover:bg-primary-100"
                      >
                        Mark Complete
                      </button>
                    )}
                  <button
                    onClick={() => {
                      setEditingClosure(closure);
                      setEditFormData({
                        closure_notes: closure.closure_notes || "",
                        client_feedback: closure.client_feedback || "",
                        client_satisfaction_rating:
                          closure.client_satisfaction_rating || "",
                        deliverables_description:
                          closure.deliverables_description || "",
                      });
                      setShowEditForm(true);
                    }}
                    className="px-3 py-1.5 text-sm bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 flex items-center gap-1"
                  >
                    <Edit size={14} /> Edit
                  </button>
                  {closure.status === "completed" && (
                    <button
                      onClick={() => handleArchive(closure.project_id)}
                      className="px-3 py-1.5 text-sm bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 flex items-center gap-1"
                    >
                      <Archive size={14} /> Archive
                    </button>
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
