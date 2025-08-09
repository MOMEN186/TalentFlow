import { useEffect, useState } from 'react';
import Card from 'react-bootstrap/Card';
import Table from 'react-bootstrap/Table';
import { useParams } from "react-router-dom";
import useAxios from '../utils/useAxios';

function EmployeeDetais() {
  const { id } = useParams();
  const api = useAxios();
  const [employee, setEmployee] = useState(null);

  useEffect(() => {
    (async () => {
      const res = await api(`/employees/${id}/`);
      setEmployee(res.data.employee);
    })();
  }, [id]);

  return (
    <div style={{ width: "100vw", minHeight: "100vh", padding: 0, margin: 0, overflow: "visible" }}>
      <Card style={{ width: "100%", margin: "0 auto", overflow: "visible", border: "none", boxShadow: "none" }}>
        <Card.Header className="text-primary">
          {employee?.first_name} {employee?.last_name} - Details
        </Card.Header>
        <Card.Body>
          {/* Personal Data */}
          <h6 className="mb-2 text-secondary">Personal Data</h6>
          <Table striped bordered hover size="sm" className="mb-4" style={{ width: "100%" }}>
            <tbody>
              <tr>
                <td>First Name</td>
                <td>{employee?.first_name}</td>
              </tr>
              <tr>
                <td>Last Name</td>
                <td>{employee?.last_name}</td>
              </tr>
              <tr>
                <td>Phone</td>
                <td>{employee?.phone}</td>
              </tr>
              <tr>
                <td>Address</td>
                <td>{employee?.address}</td>
              </tr>
              <tr>
                <td>Gender</td>
                <td>{employee?.gender}</td>
              </tr>
              <tr>
                <td>Martial State</td>
                <td>{employee?.martial_state}</td>
              </tr>
            </tbody>
          </Table>

          {/* Job Data */}
          <h6 className="mb-2 text-secondary">Job Data</h6>
          <Table striped bordered hover size="sm" className="mb-4" style={{ width: "100%" }}>
            <tbody>
              <tr>
                <td>Job Title</td>
                <td>{employee?.job_title?.name}</td>
              </tr>
              <tr>
                <td>Department</td>
                <td>{employee?.department?.name}</td>
              </tr>
              <tr>
                <td>Hire Date</td>
                <td>{employee?.date_joined}</td>
              </tr>
            </tbody>
          </Table>

          {/* Payroll Data */}
          <h6 className="mb-2 text-secondary">Payroll Data</h6>
          <Table striped bordered hover size="sm" className="mb-4" style={{ width: "100%" }}>
            <tbody>
              <tr>
                <td>Date</td>
                <td>{employee?.salary?.[0]?.date}</td>
              </tr>
              <tr>
                <td>Compensation</td>
                <td>{employee?.salary?.[0]?.compensation}</td>
              </tr>
              <tr>
                <td>Gross Pay</td>
                <td>{employee?.salary?.[0]?.gross_pay}</td>
              </tr>
              <tr>
                <td>Net Pay</td>
                <td>{employee?.salary?.[0]?.net_pay}</td>
              </tr>
              <tr>
                <td>Tax</td>
                <td>{employee?.salary?.[0]?.tax}</td>
              </tr>
              <tr>
                <td>Deduction</td>
                <td>{employee?.salary?.[0]?.deductions}</td>
              </tr>
              <tr>
                <td>Bonus</td>
                <td>{employee?.salary?.[0]?.bonus}</td>
              </tr>
            </tbody>
          </Table>

          {/* Leave Note Data */}
          <h6 className="mb-2 text-secondary">Leave Note Data</h6>
          <Table striped bordered hover size="sm" style={{ width: "100%" }}>
            <tbody>
              <tr>
                <td>Leave</td>
                <td>{employee?.leave}</td>
              </tr>
              <tr>
                <td>Reason Time Date</td>
                <td>{employee?.reason_time_date}</td>
              </tr>
              <tr>
                <td>Reason</td>
                <td>{employee?.reason}</td>
              </tr>
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </div>
  );
}
export default EmployeeDetais;
