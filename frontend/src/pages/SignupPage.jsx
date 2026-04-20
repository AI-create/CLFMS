import { useState } from "react";
import { UserPlus, Eye, EyeOff } from "lucide-react";

export default function SignupPage({ onShowLogin }) {
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    confirm_password: "",
    role: "researcher",
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [serverError, setServerError] = useState("");

  function validate() {
    const e = {};
    if (!form.email) e.email = "Email is required";
    if (!form.password) e.password = "Password is required";
    else if (form.password.length < 8) e.password = "Minimum 8 characters";
    if (form.password !== form.confirm_password)
      e.confirm_password = "Passwords do not match";
    return e;
  }

  async function handleSubmit(ev) {
    ev.preventDefault();
    const e = validate();
    if (Object.keys(e).length) {
      setErrors(e);
      return;
    }
    setErrors({});
    setServerError("");
    setLoading(true);

    try {
      const res = await fetch("/api/v1/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: form.email,
          password: form.password,
          full_name: form.full_name || undefined,
          role: form.role,
        }),
      });
      const data = await res.json();
      if (res.ok && data.success !== false) {
        setSuccess(true);
      } else {
        setServerError(data.error?.message || data.detail || "Signup failed");
      }
    } catch {
      setServerError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 w-full max-w-md text-center">
          <div className="w-16 h-16 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <UserPlus className="w-8 h-8 text-yellow-400" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">
            Request Submitted!
          </h2>
          <p className="text-slate-400 mb-2">
            Your account has been created and is <span className="text-yellow-400 font-medium">pending admin approval</span>.
          </p>
          <p className="text-slate-500 text-sm mb-6">
            The admin will review your request and send an approval. You'll be able to log in once approved.
          </p>
          <button
            onClick={onShowLogin}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors"
          >
            Back to Sign In
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-blue-600/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <UserPlus className="w-7 h-7 text-blue-400" />
          </div>
          <h1 className="text-2xl font-bold text-white">Create Account</h1>
          <p className="text-slate-400 text-sm mt-1">Join CLFMS</p>
        </div>

        {serverError && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4 text-red-400 text-sm">
            {serverError}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Full Name */}
          <div>
            <label className="block text-slate-300 text-sm font-medium mb-1.5">
              Full Name <span className="text-slate-500">(optional)</span>
            </label>
            <input
              type="text"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              placeholder="Jane Doe"
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-slate-300 text-sm font-medium mb-1.5">
              Email <span className="text-red-400">*</span>
            </label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="you@example.com"
              className={`w-full bg-slate-700 border rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors ${errors.email ? "border-red-500" : "border-slate-600"}`}
            />
            {errors.email && (
              <p className="text-red-400 text-xs mt-1">{errors.email}</p>
            )}
          </div>

          {/* Role */}
          <div>
            <label className="block text-slate-300 text-sm font-medium mb-1.5">
              Role
            </label>
            <select
              value={form.role}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-blue-500 transition-colors"
            >
              <option value="researcher">Researcher</option>
              <option value="founder">Founder</option>
            </select>
          </div>

          {/* Password */}
          <div>
            <label className="block text-slate-300 text-sm font-medium mb-1.5">
              Password <span className="text-red-400">*</span>
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                placeholder="Min. 8 characters"
                className={`w-full bg-slate-700 border rounded-lg px-4 py-2.5 pr-10 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors ${errors.password ? "border-red-500" : "border-slate-600"}`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
            {errors.password && (
              <p className="text-red-400 text-xs mt-1">{errors.password}</p>
            )}
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-slate-300 text-sm font-medium mb-1.5">
              Confirm Password <span className="text-red-400">*</span>
            </label>
            <input
              type={showPassword ? "text" : "password"}
              value={form.confirm_password}
              onChange={(e) =>
                setForm({ ...form, confirm_password: e.target.value })
              }
              placeholder="Repeat password"
              className={`w-full bg-slate-700 border rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors ${errors.confirm_password ? "border-red-500" : "border-slate-600"}`}
            />
            {errors.confirm_password && (
              <p className="text-red-400 text-xs mt-1">
                {errors.confirm_password}
              </p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-3 px-4 rounded-lg transition-colors mt-2"
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="text-center text-slate-500 text-sm mt-6">
          Already have an account?{" "}
          <button
            onClick={onShowLogin}
            className="text-blue-400 hover:text-blue-300 font-medium"
          >
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
}
