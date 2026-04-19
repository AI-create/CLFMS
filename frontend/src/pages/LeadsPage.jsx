import { useState, useEffect } from "react";
import axios from "axios";
import {
  Plus,
  Edit,
  Trash2,
  AlertCircle,
  Loader,
  Search,
  TrendingUp,
  Phone,
  Mail,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  CheckCircle,
} from "lucide-react";

const API_URL = "/api/v1";

const LEAD_STATUSES = ["new", "contacted", "qualified", "won", "lost"];
const LEAD_SOURCES = ["linkedin", "referral", "website", "email", "phone", "other"];

const STATUS_COLORS = {
  new: "bg-gray-100 text-gray-800",
  contacted: "bg-blue-100 text-blue-800",
  qualified: "bg-green-100 text-green-800",
  won: "bg-emerald-100 text-emerald-800",
  lost: "bg-red-100 text-red-800",
};

const EMPTY_FORM = {
  company_name: "",
  contact_name: "",
  contact_email: "",
  contact_phone: "",
  status: "new",
  source: "other",
  company_details: "",
  notes: "",
};

export default function LeadsPage() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [showForm, setShowForm] = useState(false);
  const [editingLead, setEditingLead] = useState(null);
  const [formData, setFormData] = useState(EMPTY_FORM);

  // Follow-up state
  const [expandedLead, setExpandedLead] = useState(null);
  const [followUps, setFollowUps] = useState({});
  const [followUpLoading, setFollowUpLoading] = useState(false);
  const [showFollowUpForm, setShowFollowUpForm] = useState(null);
  const [followUpForm, setFollowUpForm] = useState({ action: "", notes: "", scheduled_date: "" });

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/leads`);
      setLeads(response.data.data?.items || []);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load leads");
    } finally {
      setLoading(false);
    }
  };

  const fetchFollowUps = async (leadId) => {
    try {
      setFollowUpLoading(true);
      const response = await axios.get(`${API_URL}/leads/${leadId}/follow-ups`);
      const data = response.data.data;
      setFollowUps((prev) => ({ ...prev, [leadId]: Array.isArray(data) ? data : data?.items || [] }));
    } catch (err) {
      console.error("Failed to load follow-ups", err);
    } finally {
      setFollowUpLoading(false);
    }
  };

  const handleToggleExpand = async (leadId) => {
    if (expandedLead === leadId) {
      setExpandedLead(null);
    } else {
      setExpandedLead(leadId);
      if (!followUps[leadId]) {
        await fetchFollowUps(leadId);
      }
    }
  };

  const handleAddFollowUp = async (leadId, e) => {
    e.preventDefault();
    try {
      const payload = { action: followUpForm.action, notes: followUpForm.notes || null };
      if (followUpForm.scheduled_date) payload.scheduled_date = followUpForm.scheduled_date;
      await axios.post(`${API_URL}/leads/${leadId}/follow-ups`, payload);
      setShowFollowUpForm(null);
      setFollowUpForm({ action: "", notes: "", scheduled_date: "" });
      await fetchFollowUps(leadId);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to add follow-up");
    }
  };

  const handleMarkFollowUpDone = async (followUpId, leadId) => {
    try {
      await axios.put(`${API_URL}/leads/follow-ups/${followUpId}`, {
        completed_date: new Date().toISOString(),
      });
      await fetchFollowUps(leadId);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to update follow-up");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingLead) {
        await axios.put(`${API_URL}/leads/${editingLead.id}`, formData);
      } else {
        await axios.post(`${API_URL}/leads`, formData);
      }
      setShowForm(false);
      setFormData(EMPTY_FORM);
      setEditingLead(null);
      fetchLeads();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save lead");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this lead?")) return;
    try {
      await axios.delete(`${API_URL}/leads/${id}`);
      setLeads(leads.filter((l) => l.id !== id));
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete lead");
    }
  };

  const handleConvertToClient = async (id) => {
    if (!window.confirm("Convert this lead to a client?")) return;
    try {
      await axios.post(`${API_URL}/leads/${id}/convert-to-client`, {});
      fetchLeads();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to convert lead");
    }
  };

  const filteredLeads = leads.filter((lead) => {
    const term = searchTerm.toLowerCase();
    const matchesSearch =
      !searchTerm ||
      lead.contact_name?.toLowerCase().includes(term) ||
      lead.company_name?.toLowerCase().includes(term) ||
      lead.contact_email?.toLowerCase().includes(term);
    const matchesStatus = statusFilter === "all" || lead.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Leads</h1>
          <p className="text-gray-500 mt-1">Manage your sales pipeline</p>
        </div>
        <button
          onClick={() => { setEditingLead(null); setFormData(EMPTY_FORM); setShowForm(true); }}
          className="btn-primary flex items-center gap-2"
        >
          <Plus size={20} />
          New Lead
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div className="flex-1 min-w-48 relative">
          <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search leads..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="form-input w-48"
        >
          <option value="all">All Statuses</option>
          {LEAD_STATUSES.map((s) => (
            <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader className="animate-spin text-primary-600" size={32} />
        </div>
      ) : filteredLeads.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No leads found</div>
      ) : (
        <div className="space-y-3">
          {filteredLeads.map((lead) => (
            <div key={lead.id} className="bg-white rounded-lg shadow border border-gray-200">
              {/* Lead Row */}
              <div className="flex items-center justify-between px-6 py-4">
                <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <p className="font-semibold text-gray-900">{lead.contact_name}</p>
                    <p className="text-sm text-gray-500">{lead.company_name}</p>
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    {lead.contact_email && (
                      <a href={`mailto:${lead.contact_email}`} className="flex items-center gap-1 hover:text-primary-600">
                        <Mail size={14} />
                        <span className="truncate max-w-xs">{lead.contact_email}</span>
                      </a>
                    )}
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    {lead.contact_phone && (
                      <a href={`tel:${lead.contact_phone}`} className="flex items-center gap-1 hover:text-primary-600">
                        <Phone size={14} />
                        {lead.contact_phone}
                      </a>
                    )}
                  </div>
                  <div>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${STATUS_COLORS[lead.status] || "bg-gray-100 text-gray-800"}`}>
                      {lead.status}
                    </span>
                    {lead.source && (
                      <span className="ml-2 text-xs text-gray-400">{lead.source}</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-1 ml-4">
                  <button
                    onClick={() => handleToggleExpand(lead.id)}
                    className="p-2 text-gray-400 hover:text-primary-600 rounded flex items-center gap-0.5"
                    title="Follow-ups"
                  >
                    <MessageSquare size={16} />
                    {expandedLead === lead.id ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                  </button>
                  <button
                    onClick={() => handleConvertToClient(lead.id)}
                    className="p-2 text-green-600 hover:bg-green-50 rounded"
                    title="Convert to Client"
                  >
                    <TrendingUp size={16} />
                  </button>
                  <button
                    onClick={() => {
                      setEditingLead(lead);
                      setFormData({
                        company_name: lead.company_name || "",
                        contact_name: lead.contact_name || "",
                        contact_email: lead.contact_email || "",
                        contact_phone: lead.contact_phone || "",
                        status: lead.status || "new",
                        source: lead.source || "other",
                        company_details: lead.company_details || "",
                        notes: lead.notes || "",
                      });
                      setShowForm(true);
                    }}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                  >
                    <Edit size={16} />
                  </button>
                  <button
                    onClick={() => handleDelete(lead.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              {/* Follow-ups Panel */}
              {expandedLead === lead.id && (
                <div className="border-t border-gray-100 bg-gray-50 px-6 py-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-semibold text-gray-700">Follow-ups</h4>
                    <button
                      onClick={() => setShowFollowUpForm(lead.id)}
                      className="text-xs btn-primary py-1 px-2 flex items-center gap-1"
                    >
                      <Plus size={12} />
                      Add Follow-up
                    </button>
                  </div>

                  {showFollowUpForm === lead.id && (
                    <form onSubmit={(e) => handleAddFollowUp(lead.id, e)} className="mb-4 bg-white p-3 rounded border border-gray-200 space-y-2">
                      <input
                        className="form-input text-sm"
                        placeholder="Action (e.g. Call, Email, Demo)"
                        required
                        value={followUpForm.action}
                        onChange={(e) => setFollowUpForm({ ...followUpForm, action: e.target.value })}
                      />
                      <input
                        className="form-input text-sm"
                        type="datetime-local"
                        value={followUpForm.scheduled_date}
                        onChange={(e) => setFollowUpForm({ ...followUpForm, scheduled_date: e.target.value })}
                      />
                      <textarea
                        className="form-input text-sm"
                        rows={2}
                        placeholder="Notes"
                        value={followUpForm.notes}
                        onChange={(e) => setFollowUpForm({ ...followUpForm, notes: e.target.value })}
                      />
                      <div className="flex gap-2">
                        <button type="button" onClick={() => setShowFollowUpForm(null)} className="btn-secondary text-xs py-1 px-3">Cancel</button>
                        <button type="submit" className="btn-primary text-xs py-1 px-3">Save</button>
                      </div>
                    </form>
                  )}

                  {followUpLoading ? (
                    <Loader className="animate-spin text-primary-600 mx-auto my-2" size={20} />
                  ) : (followUps[lead.id] || []).length === 0 ? (
                    <p className="text-sm text-gray-400 italic">No follow-ups yet.</p>
                  ) : (
                    <div className="space-y-2">
                      {(followUps[lead.id] || []).map((fu) => (
                        <div key={fu.id} className="flex items-start justify-between bg-white rounded border border-gray-100 p-3">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              {fu.completed_date ? (
                                <CheckCircle size={14} className="text-green-500 flex-shrink-0" />
                              ) : (
                                <div className="w-3.5 h-3.5 rounded-full border-2 border-gray-300 flex-shrink-0" />
                              )}
                              <span className="text-sm font-medium text-gray-800">{fu.action}</span>
                            </div>
                            {fu.notes && <p className="text-xs text-gray-500 mt-1 ml-5">{fu.notes}</p>}
                            {fu.scheduled_date && (
                              <p className="text-xs text-gray-400 mt-1 ml-5">
                                Scheduled: {new Date(fu.scheduled_date).toLocaleString()}
                              </p>
                            )}
                            {fu.completed_date && (
                              <p className="text-xs text-green-600 mt-1 ml-5">
                                Done: {new Date(fu.completed_date).toLocaleString()}
                              </p>
                            )}
                          </div>
                          {!fu.completed_date && (
                            <button
                              onClick={() => handleMarkFollowUpDone(fu.id, lead.id)}
                              className="text-xs text-green-600 hover:underline ml-2 flex-shrink-0"
                            >
                              Mark Done
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Lead Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-semibold mb-4">
                {editingLead ? "Edit Lead" : "New Lead"}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="form-label">Company Name *</label>
                    <input
                      className="form-input"
                      type="text"
                      required
                      value={formData.company_name}
                      onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="form-label">Contact Name *</label>
                    <input
                      className="form-input"
                      type="text"
                      required
                      value={formData.contact_name}
                      onChange={(e) => setFormData({ ...formData, contact_name: e.target.value })}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="form-label">Email</label>
                    <input
                      className="form-input"
                      type="email"
                      value={formData.contact_email}
                      onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="form-label">Phone *</label>
                    <input
                      className="form-input"
                      type="tel"
                      required
                      value={formData.contact_phone}
                      onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="form-label">Status</label>
                    <select
                      className="form-input"
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    >
                      {LEAD_STATUSES.map((s) => (
                        <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="form-label">Source</label>
                    <select
                      className="form-input"
                      value={formData.source}
                      onChange={(e) => setFormData({ ...formData, source: e.target.value })}
                    >
                      {LEAD_SOURCES.map((s) => (
                        <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="form-label">Company Details</label>
                  <textarea
                    className="form-input"
                    rows={2}
                    value={formData.company_details}
                    onChange={(e) => setFormData({ ...formData, company_details: e.target.value })}
                  />
                </div>
                <div>
                  <label className="form-label">Notes</label>
                  <textarea
                    className="form-input"
                    rows={2}
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  />
                </div>
                <div className="flex gap-3 pt-2">
                  <button type="button" onClick={() => setShowForm(false)} className="btn-secondary flex-1">
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary flex-1">
                    {editingLead ? "Update" : "Create Lead"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
