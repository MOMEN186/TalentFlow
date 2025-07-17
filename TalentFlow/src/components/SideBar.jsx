// src/components/SideBar.jsx
import { useNavigate } from "react-router-dom";
import Nav from "react-bootstrap/Nav";

function SideBar() {
  const navigate = useNavigate();

  return (
    <div
      style={{
        width: "200px",
        height: "100vh",
        padding: "1rem",
        backgroundColor: "#e9ecef",
      }}
    >
      <Nav defaultActiveKey="/dashboard" className="flex-column">
        <Nav.Link onClick={() => navigate("/dashboard")}>
          Dashboard
        </Nav.Link>
        <Nav.Link onClick={() => navigate("/employees")}>
          Employees
        </Nav.Link>
        <Nav.Link onClick={() => navigate("/payroll")}>
          Payroll
        </Nav.Link>
        <Nav.Link onClick={() => navigate("/leave_note")}>
          Leave Notes
        </Nav.Link>
      </Nav>
    </div>
  );
}

export default SideBar;
