import { useEffect, useState } from "react";
import Table from "react-bootstrap/Table";
import { useNavigate, useParams } from "react-router-dom";
import useAxios from "../utils/useAxios";
import { handleDownload } from "../utils/file_download";
import Paginate from "../components/Paginate";

function Attendance() {
  const navigate = useNavigate();
  const api = useAxios();
  const [attendance, setAttendance] = useState([]);
  const page = parseInt(useParams().page||1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const getattendance = async () => {
      console.log(page);
      const response = await api.get(`/attendance/attendance/?page=${page}`);
      setAttendance(response.data.results);
      console.log(response.data);
      setTotalPages(Math.ceil(response.data.count / 50));
    };
    getattendance();
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
        <h4 className="text-primary">Attendance </h4>
        <button
          className="btn btn-success"
          onClick={() => handleDownload(api, "attendance")}
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
            <th style={{ width: "4%" }}>#</th>
            <th style={{ width: "10%" }}>First Name</th>
            <th style={{ width: "10%" }}>Last Name</th>
            <th style={{ width: "10%" }}>Middle Name</th>
            <th style={{ width: "12%" }}>Department</th>
            <th style={{ width: "12%" }}>Job Title</th>
            <th style={{ width: "12%" }}>Date</th>
            <th style={{ width: "12%" }}>check In</th>
            <th style={{ width: "12%" }}>check Out</th>
            <th style={{ width: "12%" }}>Late minutes</th>
            <th style={{ width: "12%" }}>OverTime minutes</th>
          </tr>
        </thead>
        <tbody>
          {attendance &&
            attendance.length > 0 &&
            attendance.map((emp, idx) => (
              <tr
                key={emp.id}
                onClick={() => navigate(`/employee/${emp.employee}`)}
                style={{ cursor: "pointer" }}
              >
                <td>{50 * (page - 1) + idx + 1}</td>
                <td>{emp.first_name}</td>
                <td>{emp.last_name}</td>
                <td>{emp.middle_name}</td>
                <td>{emp?.department}</td>
                <td>{emp?.job_title}</td>
                <td>{emp?.date}</td>
                <td>{emp?.check_in}</td>
                <td>{emp?.check_out}</td>
                <td>{emp?.late_minutes}</td>
                <td>{emp?.overtime_minutes}</td>
              </tr>
            ))}
        </tbody>
      </Table>
      <Paginate page={page} totalPages={totalPages} />
    </div>
  );
}

export default Attendance;
