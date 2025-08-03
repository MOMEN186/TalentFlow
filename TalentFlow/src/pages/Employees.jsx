import React from "react";
import Table from "react-bootstrap/Table";
import { useNavigate } from "react-router-dom";

function Employees() {
  const navigate = useNavigate();

  const employees = [
    { id: 1, firstName: "Mark", lastName: "Otto", department: "Engineering", jobTitle: "Software Engineer", leaveBalance: 12 },
    { id: 2, firstName: "Jacob", lastName: "Thornton", department: "Finance", jobTitle: "Accountant", leaveBalance: 8 },
    { id: 3, firstName: "Larry", lastName: "Bird", department: "HR", jobTitle: "HR Specialist", leaveBalance: 10 },
  ];

  const goToDetails = (id) => {
    navigate(`/employees/${id}`);
  };

  return (
    <div className="container mt-4">
      <h4 className="mb-4 text-primary">Employees</h4>
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Id</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Department</th>
            <th>Job Title</th>
            <th>Leave Balance</th>
          </tr>
        </thead>
        <tbody>
          {employees.map((emp) => (
            <tr
              key={emp.id}
              onClick={() => goToDetails(emp.id)}
              style={{ cursor: "pointer" }}
            >
              <td>{emp.id}</td>
              <td>{emp.firstName}</td>
              <td>{emp.lastName}</td>
              <td>{emp.department}</td>
              <td>{emp.jobTitle}</td>
              <td>{emp.leaveBalance}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}

export default Employees;
