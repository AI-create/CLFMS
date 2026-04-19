import { useState, useEffect } from "react";
import axios from "axios";
import { Plus, Edit, Trash2, AlertCircle, Loader, Search } from "lucide-react";
import PaymentForm from "../components/PaymentForm";

const API_URL = "/api/v1";

export default function PaymentsPage() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [showForm, setShowForm] = useState(false);
  const [editingPayment, setEditingPayment] = useState(null);

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/payments`);
      setPayments(response.data.data || response.data);
      setError(null);
    } catch (err) {
      console.error("Error fetching payments:", err);
      setError(err.response?.data?.detail || "Failed to load payments");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (paymentId) => {
    if (!window.confirm("Are you sure you want to delete this payment?"))
      return;

    try {
      await axios.delete(`${API_URL}/payments/${paymentId}`);
      setPayments(payments.filter((p) => p.id !== paymentId));
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete payment");
    }
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingPayment(null);
  };

  const handleFormSubmit = async () => {
    await fetchPayments();
    handleFormClose();
  };

  const filteredPayments = payments.filter((payment) => {
    const matchesSearch =
      payment.invoice_number?.includes(searchTerm) ||
      payment.payment_method?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus =
      statusFilter === "all" || payment.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    const colors = {
      pending: "bg-yellow-100 text-yellow-800",
      completed: "bg-green-100 text-green-800",
      failed: "bg-red-100 text-red-800",
      cancelled: "bg-gray-100 text-gray-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const getTotalAmount = (payments) =>
    payments.reduce((sum, p) => sum + (p.amount || 0), 0);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Payments</h1>
        <button
          onClick={() => setShowForm(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          Record Payment
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="card-lg">
          <p className="metric-label">Total Payments</p>
          <p className="metric-value text-2xl">
            ${getTotalAmount(filteredPayments).toFixed(2)}
          </p>
        </div>
        <div className="card-lg">
          <p className="metric-label">Completed Payments</p>
          <p className="metric-value text-2xl text-green-600">
            $
            {getTotalAmount(
              filteredPayments.filter((p) => p.status === "completed"),
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
            placeholder="Search payments..."
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
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {/* Payments Table */}
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
                  Payment ID
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Invoice
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Method
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Date
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
              {filteredPayments.length === 0 ? (
                <tr>
                  <td
                    colSpan="7"
                    className="px-6 py-8 text-center text-gray-500"
                  >
                    {searchTerm
                      ? "No payments match your search"
                      : "No payments found"}
                  </td>
                </tr>
              ) : (
                filteredPayments.map((payment) => (
                  <tr key={payment.id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      {payment.id}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {payment.invoice_number}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                      ${(payment.amount || 0).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {payment.payment_method || "-"}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {payment.payment_date
                        ? new Date(payment.payment_date).toLocaleDateString()
                        : "-"}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          payment.status,
                        )}`}
                      >
                        {payment.status?.charAt(0).toUpperCase() +
                          payment.status?.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <button
                        onClick={() => {
                          setEditingPayment(payment);
                          setShowForm(true);
                        }}
                        className="inline-flex items-center gap-1 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded transition"
                      >
                        <Edit size={16} />
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(payment.id)}
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
        <PaymentForm
          payment={editingPayment}
          onClose={handleFormClose}
          onSubmit={handleFormSubmit}
        />
      )}
    </div>
  );
}
