import { useState, useEffect } from "react";
import { apiError } from "../utils/apiError";
import axios from "axios";
import { Plus, Edit, Trash2, AlertCircle, Loader, Search } from "lucide-react";
import ClientForm from "../components/ClientForm";

const API_URL = "/api/v1";

export default function ClientsPage() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingClient, setEditingClient] = useState(null);

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/clients`);
      setClients(response.data.data?.data || []);
      setError(null);
    } catch (err) {
      console.error("Error fetching clients:", err);
      setError(apiError(err, "Failed to load clients"));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (clientId) => {
    if (!window.confirm("Are you sure you want to delete this client?")) return;

    try {
      await axios.delete(`${API_URL}/clients/${clientId}`);
      setClients(clients.filter((c) => c.id !== clientId));
    } catch (err) {
      setError(apiError(err, "Failed to delete client"));
    }
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingClient(null);
  };

  const handleFormSubmit = async () => {
    await fetchClients();
    handleFormClose();
  };

  const filteredClients = clients.filter(
    (client) =>
      client.company_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      client.contact_email?.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Clients</h1>
        <button
          onClick={() => setShowForm(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          Add Client
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-3 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search clients by name or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
          />
        </div>
      </div>

      {/* Clients Table */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Company Name
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Phone
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  State
                </th>
                <th className="px-6 py-3 text-right text-sm font-semibold text-gray-900">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredClients.length === 0 ? (
                <tr>
                  <td
                    colSpan="5"
                    className="px-6 py-8 text-center text-gray-500"
                  >
                    {searchTerm
                      ? "No clients match your search"
                      : "No clients found"}
                  </td>
                </tr>
              ) : (
                filteredClients.map((client) => (
                  <tr key={client.id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {client.company_name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {client.contact_email || "-"}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {client.contact_phone || "-"}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {client.state || "-"}
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <button
                        onClick={() => {
                          setEditingClient(client);
                          setShowForm(true);
                        }}
                        className="inline-flex items-center gap-1 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded transition"
                      >
                        <Edit size={16} />
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(client.id)}
                        className="inline-flex items-center gap-1 px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded transition"
                      >
                        <Trash2 size={16} />
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Form Modal */}
      {showForm && (
        <ClientForm
          client={editingClient}
          onClose={handleFormClose}
          onSubmit={handleFormSubmit}
        />
      )}
    </div>
  );
}
