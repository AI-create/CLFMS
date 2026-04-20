import { useState, useEffect } from "react";
import { apiError } from "../utils/apiError";
import axios from "axios";
import {
  Plus,
  Send,
  CheckCircle,
  AlertCircle,
  Loader,
  Search,
  Pencil,
  Trash2,
  Lock,
  Zap,
} from "lucide-react";
import InvoiceForm from "../components/InvoiceForm";
import { useProjectLocks } from "../hooks/useProjectLocks";

const API_URL = "/api/v1";

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [showForm, setShowForm] = useState(false);
  const [editingInvoice, setEditingInvoice] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [autoBillingResult, setAutoBillingResult] = useState(null);
  const { getProjectLock } = useProjectLocks();

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
      setError(apiError(err, "Failed to load invoices"));
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (invoiceId) => {
    try {
      await axios.post(`${API_URL}/invoices/${invoiceId}/send`);
      await fetchInvoices();
    } catch (err) {
      setError(apiError(err, "Failed to send invoice"));
    }
  };

  const handleMarkPaid = async (invoiceId) => {
    try {
      await axios.post(`${API_URL}/invoices/${invoiceId}/mark-paid`);
      await fetchInvoices();
    } catch (err) {
      setError(apiError(err, "Failed to mark invoice as paid"));
    }
  };

  const handleEditOpen = (invoice) => {
    setEditingInvoice(invoice);
    setEditForm({
      status: invoice.status,
      due_date: invoice.due_date ? invoice.due_date.slice(0, 10) : "",
      issued_date: invoice.issued_date ? invoice.issued_date.slice(0, 10) : "",
      subtotal: invoice.subtotal,
      cgst: invoice.cgst,
      sgst: invoice.sgst,
      igst: invoice.igst,
      total: invoice.total,
    });
    setShowEditModal(true);
  };

  const handleEditSubmit = async (e) => {
    e.preventDefault();
    if (!editingInvoice) return;
    setActionLoading(true);
    try {
      const payload = { ...editForm };
      if (!payload.due_date) delete payload.due_date;
      if (!payload.issued_date) delete payload.issued_date;
      await axios.put(`${API_URL}/invoices/${editingInvoice.id}`, payload);
      await fetchInvoices();
      setShowEditModal(false);
      setEditingInvoice(null);
    } catch (err) {
      setError(apiError(err, "Failed to update invoice"));
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;
    setActionLoading(true);
    try {
      await axios.delete(`${API_URL}/invoices/${deleteTarget.id}`);
      await fetchInvoices();
      setDeleteTarget(null);
    } catch (err) {
      setError(apiError(err, "Failed to delete invoice"));
    } finally {
      setActionLoading(false);
    }
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingInvoice(null);
  };

  const handleAutoGenerate = async () => {
    setActionLoading(true);
    setError(null);
    setAutoBillingResult(null);
    try {
      const res = await axios.post(`${API_URL}/invoices/auto-generate`);
      setAutoBillingResult(res.data.data);
      await fetchInvoices();
    } catch (err) {
      setError(apiError(err, "Auto-billing failed"));
    } finally {
      setActionLoading(false);
    }
  };

  const handleFormSubmit = async () => {
    await fetchInvoices();
    handleFormClose();
  };

  const filteredInvoices = invoices.filter((invoice) => {
    const matchesSearch =
      invoice.invoice_number
        ?.toLowerCase()
        .includes(searchTerm.toLowerCase()) ||
      String(invoice.project_id)?.includes(searchTerm);
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
        <div className="flex items-center gap-3">
          <button
            onClick={handleAutoGenerate}
            disabled={actionLoading}
            className="btn-secondary flex items-center gap-2"
            title="Auto-generate invoices for projects with billing enabled"
          >
            {actionLoading ? (
              <Loader size={16} className="animate-spin" />
            ) : (
              <Zap size={16} />
            )}
            Run Auto-Billing
          </button>
          <button
            onClick={() => setShowForm(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={20} />
            New Invoice
          </button>
        </div>
      </div>

      {/* Auto-billing result banner */}
      {autoBillingResult && (
        <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start justify-between gap-3">
          <div>
            <p className="font-medium text-green-800">
              Auto-billing complete: {autoBillingResult.generated} invoice(s)
              generated
              {autoBillingResult.errors > 0 &&
                `, ${autoBillingResult.errors} error(s)`}
            </p>
            {autoBillingResult.invoices?.length > 0 && (
              <ul className="mt-1 text-sm text-green-700 list-disc list-inside">
                {autoBillingResult.invoices.map((inv) => (
                  <li key={inv.invoice_id}>
                    {inv.invoice_number} &mdash; {inv.project_name} (
                    {inv.billing_type})
                  </li>
                ))}
              </ul>
            )}
            {autoBillingResult.generated === 0 &&
              autoBillingResult.errors === 0 && (
                <p className="text-sm text-green-700">
                  No projects were due for billing.
                </p>
              )}
          </div>
          <button
            onClick={() => setAutoBillingResult(null)}
            className="text-green-600 hover:text-green-800 text-lg font-bold leading-none"
          >
            &times;
          </button>
        </div>
      )}

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
                      Project #{invoice.project_id}
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
                      {(() => {
                        const lock = getProjectLock(invoice.project_id);
                        return (
                          <>
                            <button
                              onClick={() => {
                                if (!lock.can_edit) return;
                                handleEditOpen(invoice);
                              }}
                              disabled={!lock.can_edit}
                              title={
                                !lock.can_edit
                                  ? `Project is ${lock.status} — editing disabled`
                                  : "Edit"
                              }
                              className={`inline-flex items-center gap-1 px-3 py-1 text-sm rounded transition ${
                                lock.can_edit
                                  ? "text-gray-600 hover:bg-gray-100"
                                  : "text-gray-400 cursor-not-allowed bg-gray-50"
                              }`}
                            >
                              {lock.locked && !lock.can_edit ? (
                                <Lock size={16} />
                              ) : (
                                <Pencil size={16} />
                              )}
                              Edit
                            </button>
                            <button
                              onClick={() => {
                                if (!lock.can_delete) return;
                                setDeleteTarget(invoice);
                              }}
                              disabled={!lock.can_delete}
                              title={
                                !lock.can_delete
                                  ? `Project is ${lock.status} — deletion disabled`
                                  : "Delete"
                              }
                              className={`inline-flex items-center gap-1 px-3 py-1 text-sm rounded transition ${
                                lock.can_delete
                                  ? "text-red-600 hover:bg-red-50"
                                  : "text-gray-400 cursor-not-allowed bg-gray-50"
                              }`}
                            >
                              {lock.locked && !lock.can_delete ? (
                                <Lock size={16} />
                              ) : (
                                <Trash2 size={16} />
                              )}
                              Delete
                            </button>
                          </>
                        );
                      })()}
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

      {/* Edit Modal */}
      {showEditModal && editingInvoice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Edit Invoice {editingInvoice.invoice_number}
            </h2>
            <form onSubmit={handleEditSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  value={editForm.status}
                  onChange={(e) =>
                    setEditForm((f) => ({ ...f, status: e.target.value }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
                >
                  <option value="draft">Draft</option>
                  <option value="sent">Sent</option>
                  <option value="paid">Paid</option>
                  <option value="overdue">Overdue</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Issued Date
                </label>
                <input
                  type="date"
                  min={new Date().toISOString().split("T")[0]}
                  value={editForm.issued_date}
                  onChange={(e) =>
                    setEditForm((f) => ({ ...f, issued_date: e.target.value }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Due Date
                </label>
                <input
                  type="date"
                  min={new Date().toISOString().split("T")[0]}
                  value={editForm.due_date}
                  onChange={(e) =>
                    setEditForm((f) => ({ ...f, due_date: e.target.value }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Subtotal
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={editForm.subtotal}
                    onChange={(e) =>
                      setEditForm((f) => ({
                        ...f,
                        subtotal: parseFloat(e.target.value) || 0,
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Total
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={editForm.total}
                    onChange={(e) =>
                      setEditForm((f) => ({
                        ...f,
                        total: parseFloat(e.target.value) || 0,
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CGST
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={editForm.cgst}
                    onChange={(e) =>
                      setEditForm((f) => ({
                        ...f,
                        cgst: parseFloat(e.target.value) || 0,
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    SGST
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={editForm.sgst}
                    onChange={(e) =>
                      setEditForm((f) => ({
                        ...f,
                        sgst: parseFloat(e.target.value) || 0,
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingInvoice(null);
                  }}
                  className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="px-4 py-2 text-sm text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition disabled:opacity-50"
                >
                  {actionLoading ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirm Dialog */}
      {deleteTarget && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-sm mx-4">
            <h2 className="text-lg font-bold text-gray-900 mb-2">
              Delete Invoice
            </h2>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete invoice{" "}
              <span className="font-semibold">
                {deleteTarget.invoice_number}
              </span>
              ? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteTarget(null)}
                className="px-4 py-2 text-sm text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                disabled={actionLoading}
                className="px-4 py-2 text-sm text-white bg-red-600 hover:bg-red-700 rounded-lg transition disabled:opacity-50"
              >
                {actionLoading ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
