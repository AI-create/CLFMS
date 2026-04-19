import { Menu } from "lucide-react";

export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">CF</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">CLFMS Dashboard</h1>
        </div>
        <button className="p-2 hover:bg-gray-100 rounded-lg transition">
          <Menu size={24} className="text-gray-600" />
        </button>
      </div>
    </header>
  );
}
