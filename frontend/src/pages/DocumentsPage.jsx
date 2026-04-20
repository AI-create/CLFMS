import { useState, useEffect } from "react";
import { apiError } from "../utils/apiError";
import axios from "axios";
import {
  Plus,
  Download,
  AlertCircle,
  Loader,
  Search,
  File,
  X,
} from "lucide-react";

const API_URL = "/api/v1";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [showGenerate, setShowGenerate] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generateForm, setGenerateForm] = useState({
    type: "invoice",
    entity_id: "",
  });

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/documents`);
      setDocuments(response.data.data?.data || []);
      setError(null);
    } catch (err) {
      console.error("Error fetching documents:", err);
      setError(apiError(err, "Failed to load documents"));
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setGenerating(true);
    try {
      await axios.post(`${API_URL}/documents/generate`, generateForm);
      setShowGenerate(false);
      setGenerateForm({ type: "invoice", entity_id: "" });
      await fetchDocuments();
    } catch (err) {
      setError(apiError(err, "Failed to generate document"));
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async (doc) => {
    try {
      const response = await axios.get(
        `${API_URL}/documents/${doc.id}/download`,
        { responseType: "blob" },
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      const filename = doc.file_path?.split("/").pop() || `document_${doc.id}`;
      link.download = filename;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError("Failed to download document");
    }
  };

  const filteredDocuments = documents.filter(
    (doc) =>
      !searchTerm ||
      doc.doc_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.entity_type?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      String(doc.entity_id).includes(searchTerm),
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
        <button
          onClick={() => setShowGenerate(true)}
          className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          <Plus size={20} />
          Generate Document
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <AlertCircle className="text-red-600" size={20} />
          <p className="text-red-800">{error}</p>
          <button onClick={() => setError(null)} className="ml-auto">
            <X size={18} className="text-red-600" />
          </button>
        </div>
      )}

      {/* Generate Document Modal */}
      {showGenerate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-lg">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Generate Document
              </h2>
              <button
                onClick={() => setShowGenerate(false)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Document Type
                </label>
                <select
                  value={generateForm.type}
                  onChange={(e) =>
                    setGenerateForm({ ...generateForm, type: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="invoice">Invoice</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Entity ID (Invoice ID)
                </label>
                <input
                  type="text"
                  placeholder="Enter invoice ID"
                  value={generateForm.entity_id}
                  onChange={(e) =>
                    setGenerateForm({
                      ...generateForm,
                      entity_id: e.target.value,
                    })
                  }
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowGenerate(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={generating}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {generating ? "Generating..." : "Generate"}
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
          placeholder="Search documents..."
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
      ) : filteredDocuments.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg">
          <File className="mx-auto text-gray-400 mb-4" size={48} />
          <p className="text-gray-500">No documents found</p>
        </div>
      ) : (
        /* Documents List */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDocuments.map((doc) => (
            <div
              key={doc.id}
              className="bg-white p-4 rounded-lg shadow border border-gray-200 hover:shadow-md transition"
            >
              <div className="flex items-start gap-3 mb-3">
                <span className="text-3xl">ðŸ“„</span>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-gray-900">
                    {doc.doc_type?.toUpperCase()} #{doc.entity_id}
                  </h3>
                  <span className="inline-block text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded mt-1">
                    {doc.entity_type}
                  </span>
                </div>
              </div>

              <p className="text-xs text-gray-500 mb-3 truncate">
                {doc.file_path?.split("/").pop()}
              </p>

              <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                <span>
                  {doc.created_at
                    ? new Date(doc.created_at).toLocaleDateString()
                    : ""}
                </span>
              </div>

              <button
                onClick={() => handleDownload(doc)}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-sm"
              >
                <Download size={16} />
                Download
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
