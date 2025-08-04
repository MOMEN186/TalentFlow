import React, { useEffect } from "react";
import Table from "react-bootstrap/Table";
import { useNavigate } from "react-router-dom";
import useAxios from "../utils/useAxios";

function Employees() {
  const navigate = useNavigate();
  const api = useAxios();
  const [employees, setEmployees] = React.useState([]);

  useEffect(() => {
    const getEmployees = async () => {
      const response = await api.get("/employees/");
      console.log(response.data);
      setEmployees(response.data);
    };
    getEmployees();
  }, []);

  const goToDetails = (id) => {
    navigate(`/employees/${id}`);
  };

  useEffect(() => {
    console.log(employees);
  }, [employees]);

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
      <h4 className="mb-4 text-primary">Employees</h4>
      <Table
        striped
        bordered
        hover
        size="sm"
        style={{
          width: "100%",
          tableLayout: "fixed",
          borderCollapse: "collapse",
        }}
      >
        <thead>
          <tr>
            <th style={{ width: "4%" }}>Id</th>
            <th style={{ width: "10%" }}>First Name</th>
            <th style={{ width: "10%" }}>Last Name</th>
            <th style={{ width: "10%" }}>Middle Name</th>
            <th style={{ width: "18%" }}>Email</th>
            <th style={{ width: "14%" }}>Phone</th>
            <th style={{ width: "12%" }}>Department</th>
            <th style={{ width: "12%" }}>Job Title</th>
            <th style={{ width: "10%" }}>Leave Balance</th>
          </tr>
        </thead>
        <tbody>
          {employees &&
            employees.length > 0 &&
            employees.map((emp) => (
              <tr
                key={emp.id}
                onClick={() => goToDetails(emp.id)}
                style={{ cursor: "pointer" }}
              >
                <td>{emp.id}</td>
                <td>{emp.first_name}</td>
                <td>{emp.last_name}</td>
                <td>{emp.middle_name}</td>
                <td>{emp.email}</td>
                <td>{emp.phone}</td>
                <td>{emp.department.name}</td>
                <td>{emp.job_title.name}</td>
                <td>{emp.leaveBalance}</td>
              </tr>
            ))}
        </tbody>
      </Table>
    </div>
  );
}

export default Employees;
