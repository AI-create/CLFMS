import { useState, useEffect } from "react";
import axios from "axios";
import { AlertCircle, Loader, CheckCircle, Clock, Plus } from "lucide-react";

const API_URL = "/api/v1";

export default function OnboardingPage() {
  const [processes, setProcesses] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showInitForm, setShowInitForm] = useState(false);
  const [selectedClientId, setSelectedClientId] = useState("");
  const [initNotes, setInitNotes] = useState("");
  const [initiating, setInitiating] = useState(false);

  useEffect(() => {
    fetchOnboarding();
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      const response = await axios.get(`${API_URL}/clients`);
      setClients(response.data.data?.data || []);
    } catch (err) {
      console.error("Error fetching clients:", err);
    }
  };

  const handleInitOnboarding = async (e) => {
    e.preventDefault();
    setInitiating(true);
    try {
      await axios.post(
        `${API_URL}/onboarding/clients/${selectedClientId}/init`,
        {
          notes: initNotes,
        },
      );
      setShowInitForm(false);
      setSelectedClientId("");
      setInitNotes("");
      fetchOnboarding();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to initiate onboarding");
    } finally {
      setInitiating(false);
    }
  };

  const fetchOnboarding = async () => {
    try {
      setLoading(true);
      // Fetch all clients then get onboarding for each
      const clientsRes = await axios.get(`${API_URL}/clients`);
      const allClients = clientsRes.data.data?.data || [];
      const onboardingData = [];
      for (const client of allClients.slice(0, 20)) {
        try {
          const res = await axios.get(
            `${API_URL}/onboarding/clients/${client.id}`,
          );
          if (res.data.data) {
            onboardingData.push({
              ...res.data.data,
              client_name: client.company_name,
            });
          }
        } catch {
          // No onboarding for this client yet
        }
      }
      setProcesses(onboardingData);
      setError(null);
    } catch (err) {
      console.error("Error fetching onboarding processes:", err);
      setError(
        err.response?.data?.detail || "Failed to load onboarding processes",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (clientId, newStatus) => {
    try {
      await axios.put(`${API_URL}/onboarding/clients/${clientId}`, {
        status: newStatus,
      });
      fetchOnboarding();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update status");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Client Onboarding
          </h1>
          <p className="text-gray-600 mt-2">
            Manage client onboarding process and track progress
          </p>
        </div>
        <button
          onClick={() => setShowInitForm(true)}
          className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          <Plus size={20} />
          Init Onboarding
        </button>
      </div>

      {/* Init Form Modal */}
      {showInitForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-lg">
            <h2 className="text-xl font-bold mb-4">Start Client Onboarding</h2>
            <form onSubmit={handleInitOnboarding} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Client *
                </label>
                <select
                  value={selectedClientId}
                  onChange={(e) => setSelectedClientId(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                >
                  <option value="">Select a client</option>
                  {clients.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.company_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes
                </label>
                <textarea
                  value={initNotes}
                  onChange={(e) => setInitNotes(e.target.value)}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Optional notes..."
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
                  {initiating ? "Initiating..." : "Start Onboarding"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Loading State */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      ) : processes.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg">
          <p className="text-gray-500">No onboarding processes found</p>
          <p className="text-sm text-gray-400 mt-2">
            Use "Init Onboarding" to start a client onboarding process
          </p>
        </div>
      ) : (
        /* Onboarding Processes */
        <div className="grid gap-6">
          {processes.map((process) => (
            <div
              key={process.id}
              className="bg-white p-6 rounded-lg shadow border border-gray-200"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {process.client_name || `Client #${process.client_id}`}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Started:{" "}
                    {process.started_at
                      ? new Date(process.started_at).toLocaleDateString()
                      : "Not started"}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    process.status === "completed"
                      ? "bg-green-100 text-green-800"
                      : process.status === "in_progress"
                        ? "bg-blue-100 text-blue-800"
                        : "bg-yellow-100 text-yellow-800"
                  }`}
                >
                  {process.status}
                </span>
              </div>

              {/* Checklist Items */}
              {process.checklist_items &&
                process.checklist_items.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-900 mb-3">
                      Checklist:
                    </h4>
                    <div className="space-y-2">
                      {process.checklist_items.map((item) => (
                        <div key={item.id} className="flex items-center gap-3">
                          {item.completed_at ? (
                            <CheckCircle
                              className="text-green-600 flex-shrink-0"
                              size={20}
                            />
                          ) : (
                            <Clock
                              className="text-yellow-600 flex-shrink-0"
                              size={20}
                            />
                          )}
                          <span
                            className={
                              item.completed_at
                                ? "line-through text-gray-500"
                                : "text-gray-700"
                            }
                          >
                            {item.title}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              {process.notes && (
                <p className="text-sm text-gray-600 mb-4">{process.notes}</p>
              )}

              {/* Status Actions */}
              <div className="flex gap-2 justify-end">
                {process.status !== "completed" && (
                  <>
                    {process.status === "pending" && (
                      <button
                        onClick={() =>
                          handleStatusUpdate(process.client_id, "in_progress")
                        }
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                      >
                        Start
                      </button>
                    )}
                    {process.status === "in_progress" && (
                      <button
                        onClick={() =>
                          handleStatusUpdate(process.client_id, "completed")
                        }
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                      >
                        Mark Complete
                      </button>
                    )}
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
