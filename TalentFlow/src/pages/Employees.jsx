import  { useEffect, useState } from "react";
import Table from "react-bootstrap/Table";
import { useNavigate } from "react-router-dom";
import useAxios from "../utils/useAxios";
import { handleDownload } from "../utils/file_download";
import Paginate from "../components/Paginate";
function Employees() {
  const navigate = useNavigate();
  const api = useAxios();
  const [employees, setEmployees] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);



  useEffect(() => {
    const getEmployees = async () => {
      // console.log(page)
      const response = await api.get(`/employees/?page=${page}`);
      // console.log(response.data);
      setEmployees(response.data.results);
      setTotalPages(Math.ceil(response.data.count / 50));
    };
    getEmployees();
  }, [page]);



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
        <h4 className="text-primary">Employees </h4>
        <button
          className="btn btn-success"
          onClick={() => handleDownload(api, "employees")}
        >
          Download Excel
        </button>
      </div>
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
            <th style={{ width: "4%" }} >#</th>
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
            employees.map((emp,idx) => (
              <tr
                key={emp.id}
                onClick={() => navigate(`/employees/${emp.id}`)}
                style={{ cursor: "pointer" }}
              >
                <td>{50*(page-1)+idx+1}</td>
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
      <Paginate page={ page}  totalPages={totalPages} setPage={setPage} />
    </div>
  );
}

export default Employees;
