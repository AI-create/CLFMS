import { useState, useEffect, useRef } from "react";
import { apiError } from "../utils/apiError";
import axios from "axios";
import {
  Upload,
  Download,
  Trash2,
  AlertCircle,
  Loader,
  FileText,
} from "lucide-react";

const API_URL = "/api/v1";

const FILE_TYPES = [
  "contract",
  "agreement",
  "invoice",
  "report",
  "proposal",
  "presentation",
  "other",
];

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function FilesPage() {
  const [files, setFiles] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [searchType, setSearchType] = useState("");
  const [uploadForm, setUploadForm] = useState({
    file_type: "other",
    entity_type: "",
    entity_id: "",
    description: "",
  });
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchFiles();
  }, [searchType]);

  const fetchFiles = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = { skip: 0, limit: 50 };
      if (searchType) params.file_type = searchType;
      const response = await axios.get(`${API_URL}/files`, { params });
      const d = response.data.data;
      setFiles(d?.files || []);
      setTotal(d?.total || 0);
    } catch (err) {
      setError(apiError(err, "Failed to load files"));
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      alert("Please select a file to upload.");
      return;
    }
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);
      const params = new URLSearchParams({ file_type: uploadForm.file_type });
      if (uploadForm.entity_type)
        params.append("entity_type", uploadForm.entity_type);
      if (uploadForm.entity_id)
        params.append("entity_id", uploadForm.entity_id);
      if (uploadForm.description)
        params.append("description", uploadForm.description);
      await axios.post(`${API_URL}/files/upload?${params}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      if (fileInputRef.current) fileInputRef.current.value = "";
      setUploadForm({
        file_type: "other",
        entity_type: "",
        entity_id: "",
        description: "",
      });
      fetchFiles();
    } catch (err) {
      alert(apiError(err, "Upload failed"));
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = (fileId, fileName) => {
    const token = localStorage.getItem("token");
    const link = document.createElement("a");
    link.href = `${API_URL}/files/${fileId}/download`;
    link.download = fileName;
    link.setAttribute("type", "hidden");
    // Use fetch with auth header for download
    axios
      .get(`${API_URL}/files/${fileId}/download`, { responseType: "blob" })
      .then((res) => {
        const url = URL.createObjectURL(res.data);
        link.href = url;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      })
      .catch(() => alert("Download failed"));
  };

  const handleDelete = async (fileId) => {
    if (!confirm("Delete this file? This cannot be undone.")) return;
    try {
      await axios.delete(`${API_URL}/files/${fileId}`);
      setFiles(files.filter((f) => f.id !== fileId));
    } catch (err) {
      alert(apiError(err, "Delete failed"));
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Files</h1>
        <p className="text-gray-500 mt-1">
          Upload and manage project files and documents
        </p>
      </div>

      {/* Upload Form */}
      <div className="card-lg mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Upload size={20} />
          Upload File
        </h2>
        <form
          onSubmit={handleUpload}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          <div>
            <label className="form-label">File *</label>
            <input
              ref={fileInputRef}
              type="file"
              required
              className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100 cursor-pointer"
            />
          </div>
          <div>
            <label className="form-label">File Type</label>
            <select
              className="form-input"
              value={uploadForm.file_type}
              onChange={(e) =>
                setUploadForm({ ...uploadForm, file_type: e.target.value })
              }
            >
              {FILE_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="form-label">Entity Type</label>
            <select
              className="form-input"
              value={uploadForm.entity_type}
              onChange={(e) =>
                setUploadForm({ ...uploadForm, entity_type: e.target.value })
              }
            >
              <option value="">None</option>
              <option value="client">Client</option>
              <option value="project">Project</option>
              <option value="lead">Lead</option>
              <option value="invoice">Invoice</option>
            </select>
          </div>
          <div>
            <label className="form-label">Entity ID</label>
            <input
              className="form-input"
              type="number"
              min="1"
              placeholder="e.g. 5"
              value={uploadForm.entity_id}
              onChange={(e) =>
                setUploadForm({ ...uploadForm, entity_id: e.target.value })
              }
            />
          </div>
          <div className="sm:col-span-2 lg:col-span-1">
            <label className="form-label">Description</label>
            <input
              className="form-input"
              type="text"
              placeholder="Optional description"
              value={uploadForm.description}
              onChange={(e) =>
                setUploadForm({ ...uploadForm, description: e.target.value })
              }
            />
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              disabled={uploading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              <Upload size={18} />
              {uploading ? "Uploading..." : "Upload"}
            </button>
          </div>
        </form>
      </div>

      {/* Filter */}
      <div className="flex items-center gap-4 mb-4">
        <select
          className="form-input w-48"
          value={searchType}
          onChange={(e) => setSearchType(e.target.value)}
        >
          <option value="">All Types</option>
          {FILE_TYPES.map((t) => (
            <option key={t} value={t}>
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </option>
          ))}
        </select>
        <span className="text-sm text-gray-500">{total} file(s) total</span>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Files Table */}
      <div className="card overflow-hidden">
        {loading ? (
          <div className="flex justify-center items-center h-48">
            <Loader className="animate-spin text-primary-600" size={28} />
          </div>
        ) : files.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-gray-400">
            <FileText size={48} className="mb-2 opacity-30" />
            <p>No files found. Upload your first file above.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-200">
                  <th className="table-th">Name</th>
                  <th className="table-th">Type</th>
                  <th className="table-th">Size</th>
                  <th className="table-th">Entity</th>
                  <th className="table-th">Uploaded</th>
                  <th className="table-th">Description</th>
                  <th className="table-th">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {files.map((file) => (
                  <tr key={file.id}>
                    <td className="table-td font-medium text-gray-900">
                      {file.file_name}
                    </td>
                    <td className="table-td">
                      <span className="badge badge-blue">{file.file_type}</span>
                    </td>
                    <td className="table-td text-gray-500">
                      {formatBytes(file.file_size)}
                    </td>
                    <td className="table-td text-gray-500">
                      {file.entity_type && file.entity_id
                        ? `${file.entity_type} #${file.entity_id}`
                        : "â€”"}
                    </td>
                    <td className="table-td text-gray-500 text-sm">
                      {new Date(file.uploaded_at).toLocaleDateString()}
                    </td>
                    <td className="table-td text-gray-500 text-sm">
                      {file.description || "â€”"}
                    </td>
                    <td className="table-td">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() =>
                            handleDownload(file.id, file.file_name)
                          }
                          className="text-primary-600 hover:text-primary-800"
                          title="Download"
                        >
                          <Download size={16} />
                        </button>
                        <button
                          onClick={() => handleDelete(file.id)}
                          className="text-red-500 hover:text-red-700"
                          title="Delete"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
