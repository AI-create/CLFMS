import { useState, useEffect } from "react";
import axios from "axios";
import { Plus, Edit, Trash2, AlertCircle, Loader, Search } from "lucide-react";

const API_URL = "/api/v1";

export default function ResearchPage() {
  const [research, setResearch] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    research_type: "internal_rnd",
    objectives: "",
    status: "planned",
  });

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
      setError(err.response?.data?.detail || "Failed to load research data");
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
      setFormData({
        name: "",
        description: "",
        research_type: "internal_rnd",
        objectives: "",
        status: "planned",
      });
      setEditingItem(null);
      fetchResearch();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save research");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this research?"))
      return;

    try {
      await axios.delete(`${API_URL}/research-projects/${id}`);
      setResearch(research.filter((r) => r.id !== id));
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete research");
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
            setFormData({
              name: "",
              description: "",
              research_type: "internal_rnd",
              objectives: "",
              status: "planned",
            });
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

      {/* Research Form Modal */}
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
              className="bg-white p-6 rounded-lg shadow border border-gray-200 hover:shadow-md transition"
            >
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
                      Type: {item.research_type.replace("_", " ")}
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
                </div>
                <div className="flex gap-2">
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
          ))}
        </div>
      )}
    </div>
  );
}
