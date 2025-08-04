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
      console.log(res.data.employee);
      setEmployee(res.data.employee);
   
    })();
  }, [id]);

  useEffect(() => {
  console.log(employee)
},[employee])

  return (
    <div>
      <Card style={{ width: "28rem" }}>
        <Card.Header className="text-primary">
           {employee?.first_name}  's details
        </Card.Header>
        <Card.Body>
          <Table striped bordered hover size="sm">
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
                <td>Hire</td>
                <td>{employee?.date_joined}</td>
              </tr>
              <tr>
                <td>Leave</td>
                <td>{employee?.leave}</td>
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
                <td>Department</td>
                <td>{employee?.department?.name}</td>
              </tr>
              <tr>
                <td>Martial State</td>
                <td>{employee?.martial_state}</td>
              </tr>
              <tr>
                <td>Deduction</td>
                <td>{employee?.salary.deductions}</td>
              </tr>
              <tr>
                <td>Reason Time Date</td>
                <td>{employee?.reason_time_date}</td>
              </tr>
              <tr>
                <td>Bonus</td>
                <td>{employee?.salary.bonus}</td>
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
