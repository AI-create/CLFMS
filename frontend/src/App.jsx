import { useState } from "react";
import axios from "axios";
import Dashboard from "./pages/Dashboard";
import ClientsPage from "./pages/ClientsPage";
import ProjectsPage from "./pages/ProjectsPage";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import "./index.css";

const API_URL = "/api/v1";

export default function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [token] = useState(localStorage.getItem("token") || null);

  // Setup axios interceptor for token
  if (token) {
    axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  }

  if (!token) {
    return (
      <div className="p-8 text-center">
        Please log in to access the dashboard
      </div>
    );
  }

  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <Dashboard />;
      case "clients":
        return <ClientsPage />;
      case "projects":
        return <ProjectsPage />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto">{renderPage()}</main>
      </div>
    </div>
  );
}
