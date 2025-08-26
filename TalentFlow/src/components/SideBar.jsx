// src/components/SideBar.jsx
import { useNavigate } from "react-router-dom";
import Nav from "react-bootstrap/Nav";
import { Image } from "react-bootstrap";
import { AuthContext } from "../contexts/AuthContext";
import { useContext } from "react";

function SideBar() {
  const navigate = useNavigate();
  const { image } = useContext(AuthContext) ;
  

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
            src={image||"https://shorthand.com/the-craft/raster-images/assets/5kVrMqC0wp/sh-unsplash_5qt09yibrok-4096x2731.jpeg"}
            roundedCircle
            width={80}
            height={80}
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
