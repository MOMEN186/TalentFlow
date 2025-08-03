import Card from 'react-bootstrap/Card';
import ListGroup from 'react-bootstrap/ListGroup';
import { useParams } from "react-router-dom";

function EmployeeDetais() {
  const { id } = useParams();
  return (
    <div>
      <Card style={{ width: "18rem" }}>
        <Card.Header className='text-primary' >Employee {id}</Card.Header>
        <ListGroup variant="flush">
          <ListGroup.Item>First Name : xxx</ListGroup.Item>
          <ListGroup.Item>Last Name : xxx</ListGroup.Item>
          <ListGroup.Item>SSN : xxx</ListGroup.Item>
          <ListGroup.Item>Hire : xxx</ListGroup.Item>
          <ListGroup.Item>Leave : xxx</ListGroup.Item>
          <ListGroup.Item>Phone : xxx</ListGroup.Item>
          <ListGroup.Item>Address : xxx</ListGroup.Item>
          <ListGroup.Item>Gender : xxx</ListGroup.Item>
          <ListGroup.Item>Department : xxx</ListGroup.Item>
          <ListGroup.Item>Martial State : xxx</ListGroup.Item>
          <ListGroup.Item>Time Date : xxx</ListGroup.Item>
          <ListGroup.Item>Deduction : xxx</ListGroup.Item>
          <ListGroup.Item>Reason Time Date : xxx</ListGroup.Item>
          <ListGroup.Item>Bonus : xxx</ListGroup.Item>
          <ListGroup.Item>Reason : xxx</ListGroup.Item>
        </ListGroup>
      </Card>
    </div>
  );
}
export default EmployeeDetais;
