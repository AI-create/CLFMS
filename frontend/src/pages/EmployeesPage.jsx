import { useState, useEffect } from "react";
import axios from "axios";
import {
  Plus,
  Edit,
  Trash2,
  AlertCircle,
  Loader,
  Search,
  Clock,
  DollarSign,
  ChevronDown,
  ChevronUp,
  Activity,
  LogIn,
  LogOut,
} from "lucide-react";

const API_URL = "/api/v1";

const EMPTY_FORM = {
  name: "",
  email: "",
  employee_id: "",
  designation: "",
  department: "",
  hourly_rate: "",
};

const EMPTY_ACTIVITY_FORM = {
  activity_date: new Date().toISOString().split("T")[0],
  title: "",
  description: "",
  hours_spent: "",
  project_id: "",
  status: "in_progress",
  billable: true,
  notes: "",
};

export default function EmployeesPage() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");

  // Employee form
  const [showForm, setShowForm] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [formData, setFormData] = useState(EMPTY_FORM);

  // Expand state for activities/attendance
  const [expandedEmployee, setExpandedEmployee] = useState(null);
  const [activities, setActivities] = useState({});
  const [activitiesLoading, setActivitiesLoading] = useState(false);

  // Activity form
  const [showActivityForm, setShowActivityForm] = useState(false);
  const [activityEmpId, setActivityEmpId] = useState(null);
  const [activityForm, setActivityForm] = useState(EMPTY_ACTIVITY_FORM);
  const [activitySubmitting, setActivitySubmitting] = useState(false);

  // Clock in/out
  const [clockLoading, setClockLoading] = useState({});

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/employees`);
      setEmployees(response.data.data?.data || []);
      setError(null);
    } catch (err) {
      console.error("Error fetching employees:", err);
      setError(err.response?.data?.detail || "Failed to load employees");
    } finally {
      setLoading(false);
    }
  };

  const fetchActivities = async (empId) => {
    try {
      setActivitiesLoading(true);
      const response = await axios.get(
        `${API_URL}/employees/${empId}/activities`,
        { params: { limit: 10 } },
      );
      const d = response.data.data;
      setActivities((prev) => ({
        ...prev,
        [empId]: d?.data || [],
      }));
    } catch (err) {
      console.error("Error fetching activities:", err);
    } finally {
      setActivitiesLoading(false);
    }
  };

  const handleToggleExpand = (empId) => {
    if (expandedEmployee === empId) {
      setExpandedEmployee(null);
    } else {
      setExpandedEmployee(empId);
      if (!activities[empId]) {
        fetchActivities(empId);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingEmployee) {
        await axios.put(`${API_URL}/employees/${editingEmployee.id}`, formData);
      } else {
        await axios.post(`${API_URL}/employees`, formData);
      }
      setShowForm(false);
      setFormData(EMPTY_FORM);
      setEditingEmployee(null);
      fetchEmployees();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save employee");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this employee?"))
      return;

    try {
      await axios.delete(`${API_URL}/employees/${id}`);
      setEmployees(employees.filter((e) => e.id !== id));
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete employee");
    }
  };

  const handleClockIn = async (empId) => {
    setClockLoading((prev) => ({ ...prev, [empId]: true }));
    try {
      await axios.post(`${API_URL}/employees/${empId}/clock-in`, {
        attendance_date: new Date().toISOString().split("T")[0],
      });
      alert("Clocked in successfully!");
    } catch (err) {
      alert(err.response?.data?.detail || "Clock-in failed");
    } finally {
      setClockLoading((prev) => ({ ...prev, [empId]: false }));
    }
  };

  const handleClockOut = async (empId) => {
    setClockLoading((prev) => ({ ...prev, [empId]: true }));
    try {
      await axios.post(`${API_URL}/employees/${empId}/clock-out`, {
        break_minutes: 0,
      });
      alert("Clocked out successfully!");
    } catch (err) {
      alert(err.response?.data?.detail || "Clock-out failed");
    } finally {
      setClockLoading((prev) => ({ ...prev, [empId]: false }));
    }
  };

  const handleAddActivity = async (e) => {
    e.preventDefault();
    setActivitySubmitting(true);
    try {
      const payload = {
        activity_date: activityForm.activity_date,
        title: activityForm.title,
        hours_spent: parseFloat(activityForm.hours_spent),
        status: activityForm.status,
        billable: activityForm.billable,
      };
      if (activityForm.description) payload.description = activityForm.description;
      if (activityForm.project_id) payload.project_id = parseInt(activityForm.project_id);
      if (activityForm.notes) payload.notes = activityForm.notes;

      await axios.post(
        `${API_URL}/employees/${activityEmpId}/activities`,
        payload,
      );
      setShowActivityForm(false);
      setActivityForm(EMPTY_ACTIVITY_FORM);
      // Refresh activities for this employee
      fetchActivities(activityEmpId);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to add activity");
    } finally {
      setActivitySubmitting(false);
    }
  };

  const filteredEmployees = employees.filter(
    (emp) =>
      !searchTerm ||
      emp.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.email?.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Employees</h1>
        <button
          onClick={() => {
            setEditingEmployee(null);
            setFormData(EMPTY_FORM);
            setShowForm(true);
          }}
          className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          <Plus size={20} />
          Add Employee
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Employee Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg shadow-lg max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">
              {editingEmployee ? "Edit Employee" : "Add New Employee"}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <input
                type="text"
                placeholder="Full Name *"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
              <input
                type="email"
                placeholder="Email *"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
              <input
                type="text"
                placeholder="Employee ID (e.g. EMP001) *"
                value={formData.employee_id}
                onChange={(e) =>
                  setFormData({ ...formData, employee_id: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
              <input
                type="text"
                placeholder="Designation (e.g. Software Engineer)"
                value={formData.designation}
                onChange={(e) =>
                  setFormData({ ...formData, designation: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <input
                type="text"
                placeholder="Department"
                value={formData.department}
                onChange={(e) =>
                  setFormData({ ...formData, department: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <input
                type="number"
                placeholder="Hourly Rate"
                value={formData.hourly_rate}
                onChange={(e) =>
                  setFormData({ ...formData, hourly_rate: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
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

      {/* Activity Form Modal */}
      {showActivityForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg shadow-lg max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Log Activity</h2>
            <form onSubmit={handleAddActivity} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date *
                  </label>
                  <input
                    type="date"
                    value={activityForm.activity_date}
                    onChange={(e) =>
                      setActivityForm({
                        ...activityForm,
                        activity_date: e.target.value,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Hours Spent *
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    min="0.5"
                    placeholder="e.g. 2.5"
                    value={activityForm.hours_spent}
                    onChange={(e) =>
                      setActivityForm({
                        ...activityForm,
                        hours_spent: e.target.value,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  />
                </div>
              </div>
              <input
                type="text"
                placeholder="Activity Title *"
                value={activityForm.title}
                onChange={(e) =>
                  setActivityForm({ ...activityForm, title: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
              <textarea
                placeholder="Description"
                value={activityForm.description}
                onChange={(e) =>
                  setActivityForm({
                    ...activityForm,
                    description: e.target.value,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 min-h-16"
              />
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    value={activityForm.status}
                    onChange={(e) =>
                      setActivityForm({
                        ...activityForm,
                        status: e.target.value,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="assigned">Assigned</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="on_hold">On Hold</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Project ID
                  </label>
                  <input
                    type="number"
                    placeholder="Optional"
                    value={activityForm.project_id}
                    onChange={(e) =>
                      setActivityForm({
                        ...activityForm,
                        project_id: e.target.value,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="billable"
                  checked={activityForm.billable}
                  onChange={(e) =>
                    setActivityForm({
                      ...activityForm,
                      billable: e.target.checked,
                    })
                  }
                  className="rounded"
                />
                <label htmlFor="billable" className="text-sm text-gray-700">
                  Billable
                </label>
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowActivityForm(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={activitySubmitting}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {activitySubmitting ? "Logging..." : "Log Activity"}
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
          placeholder="Search employees..."
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
      ) : filteredEmployees.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No employees found</p>
        </div>
      ) : (
        /* Employees List */
        <div className="grid gap-4">
          {filteredEmployees.map((emp) => (
            <div
              key={emp.id}
              className="bg-white rounded-lg shadow border border-gray-200 hover:shadow-md transition"
            >
              {/* Employee Card Header */}
              <div className="p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {emp.name}
                      </h3>
                      <span className="px-2 py-0.5 bg-gray-100 rounded text-sm text-gray-600">
                        {emp.employee_id}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-medium ${
                          emp.status === "active"
                            ? "bg-green-100 text-green-800"
                            : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {emp.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{emp.email}</p>
                    <div className="flex gap-4 mt-2 text-sm text-gray-500">
                      {emp.designation && <span>{emp.designation}</span>}
                      {emp.department && <span>· {emp.department}</span>}
                      {emp.hourly_rate && (
                        <span className="flex items-center gap-1">
                          <DollarSign size={13} />
                          {emp.hourly_rate}/hr
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2 items-center">
                    {/* Clock In/Out */}
                    <button
                      onClick={() => handleClockIn(emp.id)}
                      disabled={clockLoading[emp.id]}
                      title="Clock In"
                      className="p-2 text-green-600 hover:bg-green-50 rounded disabled:opacity-50"
                    >
                      <LogIn size={18} />
                    </button>
                    <button
                      onClick={() => handleClockOut(emp.id)}
                      disabled={clockLoading[emp.id]}
                      title="Clock Out"
                      className="p-2 text-orange-600 hover:bg-orange-50 rounded disabled:opacity-50"
                    >
                      <LogOut size={18} />
                    </button>
                    <button
                      onClick={() => {
                        setActivityEmpId(emp.id);
                        setActivityForm(EMPTY_ACTIVITY_FORM);
                        setShowActivityForm(true);
                      }}
                      title="Log Activity"
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                    >
                      <Activity size={18} />
                    </button>
                    <button
                      onClick={() => handleToggleExpand(emp.id)}
                      title="Show activities"
                      className="p-2 text-gray-500 hover:bg-gray-100 rounded"
                    >
                      {expandedEmployee === emp.id ? (
                        <ChevronUp size={18} />
                      ) : (
                        <ChevronDown size={18} />
                      )}
                    </button>
                    <button
                      onClick={() => {
                        setEditingEmployee(emp);
                        setFormData({
                          name: emp.name,
                          email: emp.email,
                          employee_id: emp.employee_id || "",
                          designation: emp.designation || "",
                          department: emp.department || "",
                          hourly_rate: emp.hourly_rate || "",
                        });
                        setShowForm(true);
                      }}
                      className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                    >
                      <Edit size={18} />
                    </button>
                    <button
                      onClick={() => handleDelete(emp.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
              </div>

              {/* Activities Panel */}
              {expandedEmployee === emp.id && (
                <div className="border-t border-gray-200 p-4 bg-gray-50">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-gray-700 flex items-center gap-2">
                      <Clock size={15} />
                      Recent Activities
                    </h4>
                    <button
                      onClick={() => fetchActivities(emp.id)}
                      className="text-xs text-primary-600 hover:underline"
                    >
                      Refresh
                    </button>
                  </div>

                  {activitiesLoading ? (
                    <div className="flex justify-center py-4">
                      <Loader
                        className="animate-spin text-primary-600"
                        size={20}
                      />
                    </div>
                  ) : !activities[emp.id] ||
                    activities[emp.id].length === 0 ? (
                    <p className="text-gray-400 text-sm">
                      No activities logged yet.
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {activities[emp.id].map((act) => (
                        <div
                          key={act.id}
                          className="bg-white border border-gray-200 rounded p-3 flex items-start justify-between"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-sm text-gray-900">
                                {act.title}
                              </span>
                              <span
                                className={`px-1.5 py-0.5 rounded text-xs ${
                                  act.status === "completed"
                                    ? "bg-green-100 text-green-700"
                                    : "bg-blue-100 text-blue-700"
                                }`}
                              >
                                {act.status}
                              </span>
                              {act.billable && (
                                <span className="px-1.5 py-0.5 rounded text-xs bg-yellow-100 text-yellow-700">
                                  Billable
                                </span>
                              )}
                            </div>
                            {act.description && (
                              <p className="text-xs text-gray-500 mt-1">
                                {act.description}
                              </p>
                            )}
                          </div>
                          <div className="text-right ml-4">
                            <span className="text-sm font-semibold text-primary-600">
                              {act.hours_spent}h
                            </span>
                            <p className="text-xs text-gray-400">
                              {act.activity_date}
                            </p>
                          </div>
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
    </div>
  );
}
