import {
  Home,
  Users,
  FolderOpen,
  Receipt,
  TrendingUp,
  CheckSquare,
  PhoneIncoming,
  Briefcase,
  BookOpen,
  FileText,
  Archive,
  LogOut,
  Activity,
  Upload,
  BarChart2,
  DollarSign,
  ClipboardList,
} from "lucide-react";

export default function Sidebar({ currentPage, setCurrentPage, onLogout }) {
  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: Home },
    { id: "clients", label: "Clients", icon: Users },
    { id: "leads", label: "Leads", icon: PhoneIncoming },
    { id: "projects", label: "Projects", icon: FolderOpen },
    { id: "invoices", label: "Invoices", icon: Receipt },
    { id: "payments", label: "Payments", icon: TrendingUp },
    { id: "financial-reports", label: "Financial Reports", icon: TrendingUp },
    { id: "tasks", label: "Tasks", icon: CheckSquare },
    { id: "employees", label: "Employees", icon: Users },
    { id: "onboarding", label: "Onboarding", icon: Briefcase },
    { id: "research", label: "Research", icon: BookOpen },
    { id: "documents", label: "Documents", icon: FileText },
    { id: "closure", label: "Closure", icon: Archive },
    { id: "fiio", label: "FI-IO Tracking", icon: BarChart2 },
    { id: "files", label: "Files", icon: Upload },
    { id: "expenses", label: "Expenses", icon: DollarSign },
    { id: "operations", label: "Operations", icon: ClipboardList },
    { id: "activity-logs", label: "Activity Logs", icon: Activity },
  ];

  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center font-bold">
            CF
          </div>
          <div>
            <h1 className="font-bold text-lg">CLFMS</h1>
            <p className="text-xs text-gray-400">Client Financial</p>
          </div>
        </div>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 px-4 py-6">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;

          return (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition ${
                isActive
                  ? "bg-primary-600 text-white"
                  : "text-gray-300 hover:bg-gray-800 hover:text-white"
              }`}
            >
              <Icon size={20} />
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-6 border-t border-gray-800">
        <button
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-4 py-3 text-gray-300 hover:text-red-400 hover:bg-gray-800 rounded-lg transition"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}
