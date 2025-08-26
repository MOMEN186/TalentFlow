import { useEffect, useState } from "react";
import Table from "react-bootstrap/Table";
import { useNavigate, Link } from "react-router-dom";
import useAxios from "../utils/useAxios";
import { handleDownload } from "../utils/file_download";
import Paginate from "../components/Paginate";
import { RiDeleteBin6Line } from "react-icons/ri";
import { FaEdit } from "react-icons/fa";
import { FaUndo } from "react-icons/fa";
import { Tabs, Tab } from 'react-bootstrap'; 

function Employees() {
  const navigate = useNavigate();
  const api = useAxios();
  const [employees, setEmployees] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [currentStatus, setCurrentStatus] = useState("active"); 

  const getEmployees = async () => {
    setEmployees([]);
    let url = `http://127.0.0.1:8000/api/employees/?page=${page}&status=${currentStatus}`;
    const response = await api.get(url);
    console.log(response.data)
    setEmployees(response.data.results);
    setTotalPages(Math.ceil(response.data.count / 50));
  };

  useEffect(() => {
    getEmployees();
  }, [page, currentStatus]); 

  const handleRestore = async (empId, e) => {
    e.stopPropagation();
    const confirmRestore = window.confirm(
      "Are you sure you want to restore this employee?"
    );
    if (confirmRestore) {
      try {
        await api.patch(`http://127.0.0.1:8000/api/employees/${empId}/restore/`);
        alert("Employee has been restored successfully!");
        getEmployees();
      } catch (error) {
        console.error("Failed to restore employee:", error.response?.data);
        alert(`Error: ${error.response?.data?.error || "Unknown error"}`);
      }
    }
  };

  const handleEdit = (empId, e) => {
    e.stopPropagation();
    navigate(`/employees/edit/${empId}`);
  };

  
  const handleExit = (empId, e) => {
    e.stopPropagation();
    navigate(`/exit/add/${empId}`); 
  };

  return (
    <div
      className="mt-4"
      style={{
        flex: 1,
        width: "100%",
        padding: "0 16px",
        overflow: "auto",
        minHeight: "100vh",
      }}
    >
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4 className="text-primary">Employees</h4>
        <div>
          <button
            className="btn btn-primary me-2"
            onClick={() => navigate("/employees/add")}
          >
            Add Employee
          </button>
          <button
            className="btn btn-success"
            onClick={() => handleDownload(api, "employees")}
          >
            Download Excel
          </button>
        </div>
      </div>
      
      
      <Tabs
        id="employee-status-tabs"
        activeKey={currentStatus}
        onSelect={(k) => {
          setCurrentStatus(k);
          setPage(1); 
        }}
        className="mb-3"
      >
        <Tab eventKey="active" title="Active" />
        <Tab eventKey="pending" title="Pending" />
        <Tab eventKey="notice" title="On Notice" />
        <Tab eventKey="inactive" title="Inactive (Archived)" />
      </Tabs>

      <Table striped bordered hover size="sm">
        <thead>
          <tr>
            <th>#</th>
            <th>Id</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Department</th>
            <th>Job Title</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {employees && employees.length > 0 ? (
            employees.map((emp, idx) => (
              <tr
                key={emp.id}
                onClick={() => navigate(`/employees/${emp.id}`)}
                style={{
                  cursor: "pointer",
                  backgroundColor: emp.status === "inactive" ? "#f8d7da" : "",
                }}
              >
                <td>{50 * (page - 1) + idx + 1}</td>
                <td>{emp.id}</td>
                <td>{emp.first_name}</td>
                <td>{emp.last_name}</td>
                <td>{emp.email}</td>
                <td>{emp.phone}</td>
                <td>{emp.department?.name}</td>
                <td>{emp.job_title?.name}</td>
                <td>
                  <div style={{ display: "flex", gap: "10px" }}>
                    <FaEdit
                      onClick={(e) => handleEdit(emp.id, e)}
                      style={{ cursor: "pointer", color: "blue" }}
                    />
                    {emp.status === "inactive" ? (
                      <FaUndo
                        onClick={(e) => handleRestore(emp.id, e)}
                        style={{ cursor: "pointer", color: "green" }}
                      />
                    ) : (
                      <RiDeleteBin6Line
                        onClick={(e) => handleExit(emp.id, e)} 
                        style={{ cursor: "pointer", color: "red" }}
                      />
                    )}
                  </div>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="9" className="text-center">
                No employees found with status: {currentStatus}.
              </td>
            </tr>
          )}
        </tbody>
      </Table>
      <Paginate page={page} totalPages={totalPages} setPage={setPage} />
    </div>
  );
}

export default Employees;