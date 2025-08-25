import { useEffect, useState } from "react";
import Card from "react-bootstrap/Card";
import Table from "react-bootstrap/Table";
import Tabs from "react-bootstrap/Tabs";
import Tab from "react-bootstrap/Tab";
import { useParams } from "react-router-dom";
import useAxios from "../utils/useAxios";

function EmployeeDetais() {
  const { id } = useParams();
  const api = useAxios();

  const [employee, setEmployee] = useState(null);
  const [payrolls, setPayrolls] = useState([]);
  const [leaveNotes, setLeaveNotes] = useState([]);
  const [exitRecords, setExitRecords] = useState([]); 

  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("personal");

  useEffect(() => {
    const fetchEmployeeDetails = async () => {
      try {
        const res = await api.get(`http://127.0.0.1:8000/api/employees/${id}/`);
        setEmployee(res.data.employee);
      } catch (error) {
        console.error("Failed to fetch employee details:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchEmployeeDetails();
  }, [id]);

  useEffect(() => {
    if (activeTab === "payrolls" && payrolls.length === 0) {
      const fetchPayrolls = async () => {
        try {
          const res = await api.get(`http://127.0.0.1:8000/api/employees/${id}/payrolls/`);
          setPayrolls(res.data);
        } catch (error) {
          console.error("Failed to fetch payroll data:", error);
        }
      };
      fetchPayrolls();
    } else if (activeTab === "leave_notes" && leaveNotes.length === 0) {
      const fetchLeaveNotes = async () => {
        try {
          const res = await api.get(`http://127.0.0.1:8000/api/employees/${id}/leave-notes/`);
          setLeaveNotes(res.data);
        } catch (error) {
          console.error("Failed to fetch leave notes data:", error);
        }
      };
      fetchLeaveNotes();
    } else if (activeTab === "exit_history" && exitRecords.length === 0) { 
      const fetchExitRecords = async () => {
        try {
          const res = await api.get(`http://127.0.0.1:8000/api/employees/${id}/exit-records/`);
          setExitRecords(res.data);
        } catch (error) {
          console.error("Failed to fetch exit records data:", error);
        }
      };
      fetchExitRecords();
    }
  }, [activeTab, id, payrolls.length, leaveNotes.length, exitRecords.length]);

  if (isLoading) {
    return (
      <div style={{ padding: "20px", textAlign: "center" }}>
        <h3>Loading employee details...</h3>
      </div>
    );
  }

  if (!employee) {
    return (
      <div style={{ padding: "20px", textAlign: "center" }}>
        <h3>Employee not found or data is missing.</h3>
      </div>
    );
  }

  return (
    <div
      style={{
        width: "100%",
        minHeight: "100vh",
        padding: 0,
        margin: 0,
        overflow: "visible",
      }}
    >
      <Card
        style={{
          width: "100%",
          margin: "0 auto",
          overflow: "visible",
          border: "none",
          boxShadow: "none",
        }}
      >
        <Card.Header className="text-primary">
          {employee.first_name} {employee.last_name} - Details
          
          <span className="text-secondary ms-2">({employee.status})</span>
        </Card.Header>
        <Card.Body>
          <Tabs
            id="employee-details-tabs"
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k)}
            className="mb-3"
          >
            <Tab eventKey="personal" title="Personal & Job Data">
              <h6 className="mb-2 text-secondary">Personal Data</h6>
              <Table striped bordered hover size="sm" className="mb-4" style={{ width: "100%" }}>
                <tbody>
                  <tr><td>First Name</td><td>{employee.first_name}</td></tr>
                  <tr><td>Last Name</td><td>{employee.last_name}</td></tr>
                  <tr><td>Phone</td><td>{employee.phone}</td></tr>
                  <tr><td>Address</td><td>{employee.address}</td></tr>
                  <tr><td>Gender</td><td>{employee.gender}</td></tr>
                  <tr><td>Martial State</td><td>{employee.martial_state}</td></tr>
                </tbody>
              </Table>
              <h6 className="mb-2 text-secondary">Job Data</h6>
              <Table striped bordered hover size="sm" className="mb-4" style={{ width: "100%" }}>
                <tbody>
                  <tr><td>Job Title</td><td>{employee.job_title?.name}</td></tr>
                  <tr><td>Department</td><td>{employee.department?.name}</td></tr>
                  <tr><td>Hire Date</td><td>{employee.date_joined}</td></tr>
                  <tr><td>Status</td><td>{employee.status}</td></tr>
                </tbody>
              </Table>
            </Tab>

            <Tab eventKey="payrolls" title="Payroll History">
              <h6 className="mb-2 text-secondary">Payroll History</h6>
              <Table striped bordered hover size="sm" style={{ width: "100%" }}>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Compensation</th>
                    <th>Gross Pay</th>
                    <th>Net Pay</th>
                    <th>Tax</th>
                    <th>Bonus</th>
                    <th>Deduction</th>
                  </tr>
                </thead>
                <tbody>
                  {payrolls.length > 0 ? (
                    payrolls.map((payroll) => (
                      <tr key={payroll.id}>
                        <td>{payroll.year}-{String(payroll.month).padStart(2, '0')}</td>
                        <td>{payroll.compensation}</td>
                        <td>{payroll.gross_pay}</td>
                        <td>{payroll.net_pay}</td>
                        <td>{payroll.tax}</td>
                        <td>{payroll.bonus}</td>
                        <td>{payroll.deductions}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="text-center">No payroll records found.</td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </Tab>

            <Tab eventKey="leave_notes" title="Leave History">
              <h6 className="mb-2 text-secondary">Leave History</h6>
              <Table striped bordered hover size="sm" style={{ width: "100%" }}>
                <thead>
                  <tr>
                    <th>Leave Date</th>
                    <th>Return Date</th>
                    <th>Reason</th>
                    <th>status</th>
                  </tr>
                </thead>
                <tbody>
                  {leaveNotes.length > 0 ? (
                    leaveNotes.map((note) => (
                      <tr key={note.id}>
                        <td>{note.date}</td>
                        <td>{note.return_date}</td>
                        <td>{note.description}</td>
                        <td>{note.status}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" className="text-center">No leave notes found.</td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </Tab>

            
            <Tab eventKey="exit_history" title="Exit History">
              <h6 className="mb-2 text-secondary">Exit History</h6>
              <Table striped bordered hover size="sm" style={{ width: "100%" }}>
                <thead>
                  <tr>
                    <th>Termination Date</th>
                    <th>termination type</th>
                    <th>Reason</th>
                    <th>Notes</th>
                    <th>final settlement amount</th>
                  </tr>
                </thead>
                <tbody>
                  {exitRecords.length > 0 ? (
                    exitRecords.map((record) => (
                      <tr key={record.id}>
                        <td>{record.exit_date}</td>
                        <td>{record.exit_type}</td>
                        <td>{record.reason}</td>
                        <td>{record.notes}</td>
                        <td>{record.final_settlement_amount}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="text-center">No exit records found.</td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </Tab>

          </Tabs>
        </Card.Body>
      </Card>
    </div>
  );
}

export default EmployeeDetais;