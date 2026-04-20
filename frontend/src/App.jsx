import { useState, useEffect, Component } from "react";
import axios from "axios";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 40, fontFamily: "monospace" }}>
          <h2 style={{ color: "red" }}>Something went wrong</h2>
          <pre
            style={{
              background: "#fee",
              padding: 16,
              borderRadius: 8,
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
          >
            {this.state.error?.message}
            {"\n\n"}
            {this.state.error?.stack}
          </pre>
          <button
            onClick={() => {
              localStorage.clear();
              window.location.reload();
            }}
            style={{
              marginTop: 16,
              padding: "8px 16px",
              background: "#0284c7",
              color: "white",
              border: "none",
              borderRadius: 6,
              cursor: "pointer",
            }}
          >
            Clear session &amp; reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
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
import ProfilePage from "./pages/ProfilePage";
import SettingsPage from "./pages/SettingsPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import "./index.css";

// Pages a researcher is allowed to visit
const RESEARCHER_PAGES = new Set([
  "dashboard",
  "research",
  "tasks",
  "operations",
  "files",
  "activity-logs",
  "profile",
]);

export default function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("user");
    return stored ? JSON.parse(stored) : null;
  });
  const [showSignup, setShowSignup] = useState(false);

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

  const handleUserUpdate = (updatedUser) => {
    if (!updatedUser) return;
    setUser(updatedUser);
    localStorage.setItem("user", JSON.stringify(updatedUser));
  };

  // Guard page navigation for researcher role
  const handleSetCurrentPage = (page) => {
    if (user?.role === "researcher" && !RESEARCHER_PAGES.has(page)) {
      return; // silently block — sidebar won't show the link anyway
    }
    setCurrentPage(page);
  };

  if (!token) {
    if (showSignup) {
      return (
        <SignupPage
          onShowLogin={() => setShowSignup(false)}
          onLoginSuccess={handleLoginSuccess}
        />
      );
    }
    return (
      <LoginPage
        onLoginSuccess={handleLoginSuccess}
        onShowSignup={() => setShowSignup(true)}
      />
    );
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
      case "profile":
        return <ProfilePage user={user} onUpdate={handleUserUpdate} />;
      case "settings":
        return user?.role === "admin" || user?.role === "founder" ? (
          <SettingsPage user={user} />
        ) : (
          <Dashboard />
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <ErrorBoundary>
      <div className="flex h-screen bg-gray-50">
        <Sidebar
          currentPage={currentPage}
          setCurrentPage={handleSetCurrentPage}
          onLogout={handleLogout}
          user={user}
        />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header
            user={user}
            onLogout={handleLogout}
            setCurrentPage={handleSetCurrentPage}
          />
          <main className="flex-1 overflow-auto">
            <ErrorBoundary key={currentPage}>{renderPage()}</ErrorBoundary>
          </main>
        </div>
      </div>
    </ErrorBoundary>
  );
}
