import { useState, useEffect } from "react";
import { User, Mail, Shield, Lock, Check, X } from "lucide-react";

const ROLE_COLORS = {
  admin: "bg-red-500/20 text-red-400 border-red-500/30",
  founder: "bg-purple-500/20 text-purple-400 border-purple-500/30",
  researcher: "bg-blue-500/20 text-blue-400 border-blue-500/30",
};

export default function ProfilePage({ user, onUpdate }) {
  const token = localStorage.getItem("token");

  const [info, setInfo] = useState({
    full_name: user?.full_name || "",
    email: user?.email || "",
  });
  const [pwForm, setPwForm] = useState({
    current_password: "",
    new_password: "",
    confirm: "",
  });
  const [saving, setSaving] = useState(false);
  const [pwSaving, setPwSaving] = useState(false);
  const [infoMsg, setInfoMsg] = useState(null);
  const [pwMsg, setPwMsg] = useState(null);

  useEffect(() => {
    setInfo({ full_name: user?.full_name || "", email: user?.email || "" });
  }, [user]);

  async function saveInfo(ev) {
    ev.preventDefault();
    setSaving(true);
    setInfoMsg(null);
    try {
      const res = await fetch("/api/v1/auth/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          full_name: info.full_name || null,
          email: info.email || null,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setInfoMsg({ ok: true, text: "Profile updated" });
        if (onUpdate) onUpdate(data.data);
      } else {
        setInfoMsg({ ok: false, text: data.error?.message || "Update failed" });
      }
    } catch {
      setInfoMsg({ ok: false, text: "Network error" });
    } finally {
      setSaving(false);
    }
  }

  async function savePassword(ev) {
    ev.preventDefault();
    if (pwForm.new_password !== pwForm.confirm) {
      setPwMsg({ ok: false, text: "New passwords do not match" });
      return;
    }
    if (pwForm.new_password.length < 8) {
      setPwMsg({ ok: false, text: "Password must be at least 8 characters" });
      return;
    }
    setPwSaving(true);
    setPwMsg(null);
    try {
      const res = await fetch("/api/v1/auth/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: pwForm.current_password,
          new_password: pwForm.new_password,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setPwMsg({ ok: true, text: "Password changed successfully" });
        setPwForm({ current_password: "", new_password: "", confirm: "" });
      } else {
        setPwMsg({
          ok: false,
          text: data.error?.message || "Password change failed",
        });
      }
    } catch {
      setPwMsg({ ok: false, text: "Network error" });
    } finally {
      setPwSaving(false);
    }
  }

  const initials = (user?.full_name || user?.email || "?")
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      {/* Header card */}
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 flex items-center gap-5">
        <div className="w-16 h-16 rounded-full bg-blue-600 flex items-center justify-center text-white text-xl font-bold flex-shrink-0">
          {initials}
        </div>
        <div className="min-w-0">
          <h1 className="text-xl font-bold text-white truncate">
            {user?.full_name || user?.email}
          </h1>
          <p className="text-slate-400 text-sm truncate">{user?.email}</p>
          <span
            className={`inline-flex items-center gap-1 mt-1 px-2 py-0.5 rounded-full border text-xs font-medium ${ROLE_COLORS[user?.role] || "bg-slate-600 text-slate-300 border-slate-500"}`}
          >
            <Shield className="w-3 h-3" />
            {user?.role}
          </span>
        </div>
        {user?.created_at && (
          <div className="ml-auto text-right flex-shrink-0">
            <p className="text-xs text-slate-500">Member since</p>
            <p className="text-sm text-slate-300">
              {new Date(user.created_at).toLocaleDateString()}
            </p>
          </div>
        )}
      </div>

      {/* Edit profile */}
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <User className="w-5 h-5 text-blue-400" /> Edit Profile
        </h2>
        <form onSubmit={saveInfo} className="space-y-4">
          <div>
            <label className="block text-slate-300 text-sm font-medium mb-1.5">
              Full Name
            </label>
            <input
              type="text"
              value={info.full_name}
              onChange={(e) => setInfo({ ...info, full_name: e.target.value })}
              placeholder="Your name"
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
          <div>
            <label className="block text-slate-300 text-sm font-medium mb-1.5">
              <Mail className="w-4 h-4 inline mr-1" />
              Email
            </label>
            <input
              type="email"
              value={info.email}
              onChange={(e) => setInfo({ ...info, email: e.target.value })}
              placeholder="your@email.com"
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
          {infoMsg && (
            <div
              className={`flex items-center gap-2 text-sm p-3 rounded-lg ${infoMsg.ok ? "bg-green-500/10 border border-green-500/30 text-green-400" : "bg-red-500/10 border border-red-500/30 text-red-400"}`}
            >
              {infoMsg.ok ? (
                <Check className="w-4 h-4" />
              ) : (
                <X className="w-4 h-4" />
              )}
              {infoMsg.text}
            </div>
          )}
          <button
            type="submit"
            disabled={saving}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-2.5 px-6 rounded-lg transition-colors"
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </form>
      </div>

      {/* Change password */}
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Lock className="w-5 h-5 text-blue-400" /> Change Password
        </h2>
        <form onSubmit={savePassword} className="space-y-4">
          <div>
            <label className="block text-slate-300 text-sm font-medium mb-1.5">
              Current Password
            </label>
            <input
              type="password"
              value={pwForm.current_password}
              onChange={(e) =>
                setPwForm({ ...pwForm, current_password: e.target.value })
              }
              placeholder="••••••••"
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
          <div>
            <label className="block text-slate-300 text-sm font-medium mb-1.5">
              New Password
            </label>
            <input
              type="password"
              value={pwForm.new_password}
              onChange={(e) =>
                setPwForm({ ...pwForm, new_password: e.target.value })
              }
              placeholder="Min. 8 characters"
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
          <div>
            <label className="block text-slate-300 text-sm font-medium mb-1.5">
              Confirm New Password
            </label>
            <input
              type="password"
              value={pwForm.confirm}
              onChange={(e) =>
                setPwForm({ ...pwForm, confirm: e.target.value })
              }
              placeholder="Repeat new password"
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>
          {pwMsg && (
            <div
              className={`flex items-center gap-2 text-sm p-3 rounded-lg ${pwMsg.ok ? "bg-green-500/10 border border-green-500/30 text-green-400" : "bg-red-500/10 border border-red-500/30 text-red-400"}`}
            >
              {pwMsg.ok ? (
                <Check className="w-4 h-4" />
              ) : (
                <X className="w-4 h-4" />
              )}
              {pwMsg.text}
            </div>
          )}
          <button
            type="submit"
            disabled={pwSaving}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-2.5 px-6 rounded-lg transition-colors"
          >
            {pwSaving ? "Updating..." : "Update Password"}
          </button>
        </form>
      </div>
    </div>
  );
}
