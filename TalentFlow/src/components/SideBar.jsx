// src/components/SideBar.jsx
import { useNavigate } from "react-router-dom";
import Nav from "react-bootstrap/Nav";
import { Image } from "react-bootstrap";

function SideBar() {
  const navigate = useNavigate();

  return (
    <div
      style={{
        width: "200px",
        height: "150vh",
        padding: "1rem",
        backgroundColor: "#e9ecef",
      }}
    >
      <Nav defaultActiveKey="/dashboard" className="flex-column">
        <Nav.Link onClick={() => navigate("/profile")}>
          <Image
            src="https://www.bigfootdigital.co.uk/how-to-optimise-images"
            roundedCircle
          />
        </Nav.Link>
        <Nav.Link onClick={() => navigate("/dashboard")}>Dashboard</Nav.Link>
        <Nav.Link onClick={() => navigate("/employees")}>Employees</Nav.Link>
        <Nav.Link onClick={() => navigate("/payroll")}>Payroll</Nav.Link>
        <Nav.Link onClick={() => navigate("/leave_note")}>Leave Notes</Nav.Link>
        <Nav.Link onClick={() => navigate("/attendance")}>Attendance</Nav.Link>
      </Nav>
    </div>
  );
}

export default SideBar;
