// src/App.jsx
import { Route, Routes } from "react-router-dom";
import SideBar from "./components/SideBar";
import Employees from "./pages/Employees";
import Dashboard from "./pages/Dashboard";
import PayRoll from "./pages/Payroll";     
import NotFound from "./pages/NotFound";
import LeaveNote from "./pages/LeaveNote";
function App() {
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <SideBar />
      <div style={{ flex: 1, overflowY: "auto" }}>
        <div className="container my-3">
          <Routes>
            <Route path="/" element={<Employees />} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/payroll" element={<PayRoll/>} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/leave_note" element={<LeaveNote/>} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

export default App;
