// src/App.jsx
import { Route, Routes, useNavigate } from "react-router-dom";
import SideBar from "./components/SideBar";
import Employees from "./pages/Employees";
import Dashboard from "./pages/Dashboard";
import PayRoll from "./pages/Payroll";     
import NotFound from "./pages/NotFound";
import LeaveNote from "./pages/LeaveNote";
import Login from "./pages/Login";
import { createContext, useEffect, useState } from "react";
// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext();
function App() {
  const [user, setUser] = useState({});

  const navigate = useNavigate();
  useEffect(() => {
    if (!user || !user.email || !user.refresh) {
      navigate("/login")
    }
  }, [user]);
  
  return (
    <AuthContext.Provider value={{ user, setUser }}>
    <div style={{ display: "flex", height: "100vh" }}>
      <SideBar />
      <div style={{ flex: 1, overflowY: "auto" }}>
        <div className="container my-3">
          <Routes>
            <Route path="/" element={<Employees />} />
            <Route path="/login" element={ <Login/>} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/payroll" element={<PayRoll/>} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/leave_note" element={<LeaveNote/>} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </div>
      </div>
      </AuthContext.Provider>
  );
}

export default App;
