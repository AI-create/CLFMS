import { useState, useEffect } from "react";
import axios from "axios";
import Dashboard from "./pages/Dashboard";
import ClientsPage from "./pages/ClientsPage";
import ProjectsPage from "./pages/ProjectsPage";
import InvoicesPage from "./pages/InvoicesPage";
import PaymentsPage from "./pages/PaymentsPage";
import FinancialReportsPage from "./pages/FinancialReportsPage";
import TasksPage from "./pages/TasksPage";
import EmployeesPage from "./pages/EmployeesPage";
import LeadsPage from "./pages/LeadsPage";
import OnboardingPage from "./pages/OnboardingPage";
import ResearchPage from "./pages/ResearchPage";
import DocumentsPage from "./pages/DocumentsPage";
import ClosurePage from "./pages/ClosurePage";
import FiioPage from "./pages/FiioPage";
import FilesPage from "./pages/FilesPage";
import ActivityLogsPage from "./pages/ActivityLogsPage";
import ExpensesPage from "./pages/ExpensesPage";
import OperationsPage from "./pages/OperationsPage";
import LoginPage from "./pages/LoginPage";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import "./index.css";

const API_URL = "/api/v1";

export default function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });

  // Setup axios interceptor for token
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common["Authorization"];
    }
  }, [token]);

  const handleLoginSuccess = (newToken, newUser) => {
    setToken(newToken);
    setUser(newUser);
    setCurrentPage("dashboard");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common["Authorization"];
  };

  if (!token) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <Dashboard />;
      case "clients":
        return <ClientsPage />;
      case "leads":
        return <LeadsPage />;
      case "projects":
        return <ProjectsPage />;
      case "invoices":
        return <InvoicesPage />;
      case "payments":
        return <PaymentsPage />;
      case "financial-reports":
        return <FinancialReportsPage />;
      case "tasks":
        return <TasksPage />;
      case "employees":
        return <EmployeesPage />;
      case "onboarding":
        return <OnboardingPage />;
      case "research":
        return <ResearchPage />;
      case "documents":
        return <DocumentsPage />;
      case "closure":
        return <ClosurePage />;
      case "fiio":
        return <FiioPage />;
      case "files":
        return <FilesPage />;
      case "activity-logs":
        return <ActivityLogsPage />;
      case "expenses":
        return <ExpensesPage />;
      case "operations":
        return <OperationsPage />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        onLogout={handleLogout}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header user={user} onLogout={handleLogout} />
        <main className="flex-1 overflow-auto">{renderPage()}</main>
      </div>
    </div>
  );
}
