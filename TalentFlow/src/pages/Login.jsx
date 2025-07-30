import Form from "react-bootstrap/Form";
import { useContext, useState } from "react";
import Button from "react-bootstrap/Button";
import { AuthContext } from "../contexts/AuthContext";
function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useContext(AuthContext);
  const handleClick = async (e) => {
    e.preventDefault();
    login(email,password);
  };

  return (
    <Form>
      <Form.Group className="mb-3" controlId="formGroupEmail">
        <Form.Label>Email address</Form.Label>
        <Form.Control
          type="email"
          placeholder="Enter email"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
          }}
        />
      </Form.Group>
      <Form.Group className="mb-3" controlId="formGroupPassword">
        <Form.Label>Password</Form.Label>
        <Form.Control
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
          }}
        />
      </Form.Group>
      <Form.Group className="mb-3" controlId="formGroupPassword">
        <Button
          as="input"
          type="submit"
          value="Submit"
          onClick={(e) => handleClick(e)}
        />
      </Form.Group>
    </Form>
  );
}

export default Login;
