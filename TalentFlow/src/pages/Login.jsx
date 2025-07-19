import Form from "react-bootstrap/Form";
import { useContext, useEffect, useState } from "react";
import Button from "react-bootstrap/Button";
import { login } from "../controllers/loginController";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../App";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const { user, setUser } = useContext(AuthContext);

  const handleClick = async (e) => {
    e.preventDefault();
    const res = await login(email, password);
    setUser({
      email,
      access: res.access,
      refresh: res.refresh,
    });
    navigate("/");
    };
    

    useEffect(() => {
        console.log(user);
    }, [user]);

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
