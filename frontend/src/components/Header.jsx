import { Menu, LogOut, User, Settings } from "lucide-react";
import { useState } from "react";

export default function Header({ user, onLogout, setCurrentPage }) {
  const [showMenu, setShowMenu] = useState(false);
  const role = user?.role;
  const displayName = user?.full_name || user?.email || "User";

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">CF</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">CLFMS Dashboard</h1>
        </div>
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-2 hover:bg-gray-100 rounded-lg transition flex items-center gap-2"
          >
            <div className="text-right mr-2">
              <p className="text-sm font-medium text-gray-900 truncate max-w-[140px]">
                {displayName}
              </p>
              <p className="text-xs text-gray-500 capitalize">{role}</p>
            </div>
            <Menu size={24} className="text-gray-600" />
          </button>

          {/* Dropdown Menu */}
          {showMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
              <button
                onClick={() => {
                  setShowMenu(false);
                  setCurrentPage?.("profile");
                }}
                className="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
              >
                <User size={16} />
                Profile
              </button>
              {(role === "admin" || role === "founder") && (
                <button
                  onClick={() => {
                    setShowMenu(false);
                    setCurrentPage?.("settings");
                  }}
                  className="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                >
                  <Settings size={16} />
                  Settings
                </button>
              )}
              <button
                onClick={() => {
                  setShowMenu(false);
                  onLogout();
                }}
                className="w-full px-4 py-3 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 border-t border-gray-200"
              >
                <LogOut size={16} />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
