import { Route, Routes } from "react-router-dom";
import SideBar from "./components/SideBar";
import Employees from "./pages/Employees";
import Dashboard from "./pages/Dashboard";
import PayRoll from "./pages/Payroll";
import NotFound from "./pages/NotFound";
import LeaveNote from "./pages/LeaveNote";
import EmployeeDetais from "./pages/EmployeeDetails";
import Login from "./pages/Login";
import { AuthProvider } from "./providers/AuthProvider";
import Profile from "./pages/Profile";
import ProtectedRoute from "./components/ProtectedRoute";
import Attendance from "./pages/Attendance";

function App() {
  return (
    <AuthProvider>
      <div style={{ display: "flex", height: "100vh" }}>
        <SideBar />
        <div style={{ flex: 1, overflowY: "auto" }}>
          <div className="my-3" style={{ width: '100%' }}>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={<ProtectedRoute element={<Dashboard />} />} />
              <Route path="/dashboard" element={<ProtectedRoute element={<Dashboard />} />} />
              <Route path="/employees/:page?" element={<ProtectedRoute element={<Employees />} />} />
              <Route path="/employees/:id" element={<ProtectedRoute element={<EmployeeDetais />} />} />
              <Route path="/payroll/:page?" element={<ProtectedRoute element={<PayRoll />} />} />
              <Route path="/leave_note/:page?" element={<ProtectedRoute element={<LeaveNote />} />} />
              <Route path="/profile" element={<ProtectedRoute element={<Profile />} />} />
              <Route path="/attendance/:page?" element={<ProtectedRoute element={<Attendance />} />} />

              <Route path="*" element={<ProtectedRoute element={<NotFound />} />} />
            </Routes>
          </div>
        </div>
      </div>
    </AuthProvider>
  );
}

export default App;
