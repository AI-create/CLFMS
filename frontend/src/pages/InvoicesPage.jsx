import { useState, useEffect } from "react";
import axios from "axios";
import {
  Plus,
  Eye,
  Send,
  CheckCircle,
  AlertCircle,
  Loader,
  Search,
} from "lucide-react";
import InvoiceForm from "../components/InvoiceForm";

const API_URL = "/api/v1";

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [showForm, setShowForm] = useState(false);
  const [editingInvoice, setEditingInvoice] = useState(null);

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/invoices`);
      setInvoices(response.data.data?.data || []);
      setError(null);
    } catch (err) {
      console.error("Error fetching invoices:", err);
      setError(err.response?.data?.detail || "Failed to load invoices");
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (invoiceId) => {
    try {
      await axios.post(`${API_URL}/invoices/${invoiceId}/send`);
      await fetchInvoices();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to send invoice");
    }
  };

  const handleMarkPaid = async (invoiceId) => {
    try {
      await axios.post(`${API_URL}/invoices/${invoiceId}/mark-paid`);
      await fetchInvoices();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to mark invoice as paid");
    }
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingInvoice(null);
  };

  const handleFormSubmit = async () => {
    await fetchInvoices();
    handleFormClose();
  };

  const filteredInvoices = invoices.filter((invoice) => {
    const matchesSearch =
      invoice.invoice_number?.includes(searchTerm) ||
      invoice.client_name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus =
      statusFilter === "all" || invoice.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    const colors = {
      draft: "bg-gray-100 text-gray-800",
      sent: "bg-blue-100 text-blue-800",
      paid: "bg-green-100 text-green-800",
      overdue: "bg-red-100 text-red-800",
      cancelled: "bg-gray-200 text-gray-600",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const getTotalAmount = (invoices) =>
    invoices.reduce((sum, i) => sum + (i.total || 0), 0);
  const getPaidAmount = (invoices) =>
    invoices
      .filter((i) => i.status === "paid")
      .reduce((sum, i) => sum + (i.total || 0), 0);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Invoices</h1>
        <button
          onClick={() => setShowForm(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          New Invoice
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="card-lg">
          <p className="metric-label">Total Invoices</p>
          <p className="metric-value text-2xl">
            ${getTotalAmount(filteredInvoices).toFixed(2)}
          </p>
        </div>
        <div className="card-lg">
          <p className="metric-label">Paid</p>
          <p className="metric-value text-2xl text-green-600">
            ${getPaidAmount(filteredInvoices).toFixed(2)}
          </p>
        </div>
        <div className="card-lg">
          <p className="metric-label">Outstanding</p>
          <p className="metric-value text-2xl text-red-600">
            $
            {(
              getTotalAmount(filteredInvoices) - getPaidAmount(filteredInvoices)
            ).toFixed(2)}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-3 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search invoices..."
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
          <option value="all">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="sent">Sent</option>
          <option value="paid">Paid</option>
          <option value="overdue">Overdue</option>
        </select>
      </div>

      {/* Invoices Table */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Invoice #
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Client
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Due Date
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-sm font-semibold text-gray-900">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredInvoices.length === 0 ? (
                <tr>
                  <td
                    colSpan="6"
                    className="px-6 py-8 text-center text-gray-500"
                  >
                    {searchTerm
                      ? "No invoices match your search"
                      : "No invoices found"}
                  </td>
                </tr>
              ) : (
                filteredInvoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {invoice.invoice_number}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {invoice.client_name}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      ${(invoice.total || 0).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {invoice.due_date
                        ? new Date(invoice.due_date).toLocaleDateString()
                        : "-"}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          invoice.status,
                        )}`}
                      >
                        {invoice.status?.charAt(0).toUpperCase() +
                          invoice.status?.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      {invoice.status === "draft" && (
                        <button
                          onClick={() => handleSend(invoice.id)}
                          className="inline-flex items-center gap-1 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded transition"
                        >
                          <Send size={16} />
                          Send
                        </button>
                      )}
                      {invoice.status !== "paid" && (
                        <button
                          onClick={() => handleMarkPaid(invoice.id)}
                          className="inline-flex items-center gap-1 px-3 py-1 text-sm text-green-600 hover:bg-green-50 rounded transition"
                        >
                          <CheckCircle size={16} />
                          Mark Paid
                        </button>
                      )}
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
        <InvoiceForm onClose={handleFormClose} onSubmit={handleFormSubmit} />
      )}
    </div>
  );
}
