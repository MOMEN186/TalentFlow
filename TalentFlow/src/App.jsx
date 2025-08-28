import { Route, Routes } from "react-router-dom";
import SideBar from "./components/SideBar";
import AddExit from "./pages/AddExit";
import AddEmployee from "./pages/AddEmployee";
import EmployeeDetais from "./pages/EmployeeDetails";
import Employees from "./pages/Employees";
import Dashboard from "./pages/Dashboard";
import PayRoll from "./pages/Payroll";
import AddPayroll from "./pages/AddPayroll";
import NotFound from "./pages/NotFound";
import LeaveNote from "./pages/LeaveNote";
import AddLeaveNote from "./pages/AddLeaveNote";
import Login from "./pages/Login";
import { AuthProvider } from "./providers/AuthProvider";
import Profile from "./pages/Profile";
import ProtectedRoute from "./components/ProtectedRoute";
import Attendance from "./pages/Attendance";
import AddEditAttendance from "./pages/AddEditAttendance"; 

function App() {
  return (
    <AuthProvider>
      <div style={{ display: "flex", minHeight: "100vh", width: "100vw" }}>
        <SideBar />
        <div style={{
          flex: 1,
          width: "100%",
          height: "100%",
          overflow: "auto",
          minWidth: 0, // prevents shrinking
          padding: 0,
          margin: 0,
          background: "#fff"
        }}>
          <div className="my-3" style={{ width: '100%' }}>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/" element={<ProtectedRoute element={<Dashboard />} />} />
              <Route path="/dashboard" element={<ProtectedRoute element={<Dashboard />} />} />
              <Route path="/exit/add/:employeeId" element={<AddExit />} />
              <Route path="/employees/:id" element={<ProtectedRoute element={<EmployeeDetais />} />} />
              <Route path="/employees/add" element={<AddEmployee />} />
              <Route path="/employees/edit/:id" element={<AddEmployee />} />
              <Route path="/employees/:page?" element={<ProtectedRoute element={<Employees />} />} />
              <Route path="/payroll/:page?" element={<ProtectedRoute element={<PayRoll />} />} />
              <Route path="/payroll/add" element={<AddPayroll />} />
              <Route path="/payroll/edit/:id" element={<AddPayroll />} />
              <Route path="/leave_note/:page?" element={<ProtectedRoute element={<LeaveNote />} />} />
              <Route path="/leave_notes/add" element={<AddLeaveNote />} />
              <Route path="/profile" element={<ProtectedRoute element={<Profile />} />} />
              <Route path="/attendance/:page?" element={<ProtectedRoute element={<Attendance />} />} />
              <Route path="/attendance/add" element={<AddEditAttendance />} />
              <Route path="/attendance/edit/:id" element={<AddEditAttendance />} />
              <Route path="*" element={<ProtectedRoute element={<NotFound />} />} />
            </Routes>
          </div>
        </div>
      </div>
    </AuthProvider>
  );
}

export default App;
