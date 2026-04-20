import { useState } from "react";
import { apiError } from "../utils/apiError";
import axios from "axios";
import { AlertCircle, Loader } from "lucide-react";

const API_URL = "/api/v1";

export default function LoginPage({ onLoginSuccess }) {
  const [email, setEmail] = useState("admin@clfms.local");
  const [password, setPassword] = useState("admin123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        password,
      });

      const { token, user } = response.data.data;

      // Store token and user info
      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(user));

      // Update axios default header
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;

      // Call callback
      onLoginSuccess(token, user);
    } catch (err) {
      setError(
        apiError(
          err,
          err.message || "Failed to login. Please check your credentials.",
        ),
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-white rounded-lg shadow-2xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">CLFMS</h1>
            <p className="text-gray-600">Client Financial Management System</p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error */}
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
                <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@clfms.local"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
                disabled={loading}
              />
              <p className="mt-1 text-xs text-gray-500">
                Demo: admin@clfms.local
              </p>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="password"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
                disabled={loading}
              />
              <p className="mt-1 text-xs text-gray-500">Demo: admin123</p>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded-lg transition flex items-center justify-center gap-2"
            >
              {loading && <Loader size={20} className="animate-spin" />}
              {loading ? "Logging in..." : "Sign In"}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-8 pt-8 border-t border-gray-200 text-center text-sm text-gray-600">
            <p>Demo Credentials</p>
            <p className="mt-2">
              <strong>Email:</strong> admin@clfms.local
            </p>
            <p>
              <strong>Password:</strong> password
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
