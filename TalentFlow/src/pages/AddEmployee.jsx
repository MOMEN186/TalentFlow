import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import useAxios from "../utils/useAxios";
import { Form, Button, Card, Spinner, Alert, Row, Col } from "react-bootstrap";

function AddEmployee() {
  const { id } = useParams();
  const navigate = useNavigate();
  const api = useAxios();
  const isEditing = !!id;
  const [formData, setFormData] = useState({
    first_name: "",
    middle_name: "",
    last_name: "",
    gender: "",
    email: "",
    phone: "",
    address: "",
    department: "",
    job_title: "",
    password: "",
    password2: "",
    is_hr: false,
    status: "binding", 
  });
  const [departments, setDepartments] = useState([]);
  const [jobTitles, setJobTitles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [deptsRes, jobsRes] = await Promise.all([
          api.get("api/departments/"),
          api.get("api/job-titles/"),
        ]);
        setDepartments(deptsRes.data.results);
        setJobTitles(jobsRes.data.results);

        if (isEditing) {
          try {
            const employeeResponse = await api.get(`/api/employees/${id}/`);
            const employeeData = employeeResponse.data.employee;
            setFormData((prevData) => ({
              ...prevData,
              first_name: employeeData.first_name,
              middle_name: employeeData.middle_name || "",
              last_name: employeeData.last_name,
              gender: employeeData.gender,
              email: employeeData.email,
              phone: employeeData.phone,
              address: employeeData.address,
              department: employeeData.department.id,
              job_title: employeeData.job_title.id,
              is_hr: employeeData.is_hr,
              status: employeeData.status, 
              password: "",
              password2: "",
            }));
          } catch (err) {
            if (err.response && err.response.status === 404) {
              setError("Employee not found.");
              setTimeout(() => navigate("/employees"), 3000);
            } else {
              setError("Failed to load employee data.");
            }
          }
        }
      } catch (err) {
        console.error("Failed to fetch initial data:", err);
        setError("Failed to load departments and job titles.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [id, isEditing, navigate]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
  e.preventDefault();
  setIsLoading(true);
  setError(null);

  
  if (!formData.department) {
    setError("Please select a department.");
    setIsLoading(false);
    return;
  }
  if (!formData.job_title) {
    setError("Please select a job title.");
    setIsLoading(false);
    return;
  }
  if (!isEditing && formData.password !== formData.password2) {
    setError("Passwords do not match.");
    setIsLoading(false);
    return;
  }

  try {
    
    const isHrData = { is_hr: formData.is_hr };
    const employeeData = { ...formData };
    delete employeeData.is_hr; 
    delete employeeData.password2;

    if (isEditing) {
      
      if (!employeeData.password) {
        delete employeeData.password;
      }
      await api.patch(`/api/employees/${id}/update_is_hr/`, isHrData);
      await api.patch(`/api/employees/${id}/`, employeeData);
      alert("Employee updated successfully!");
      navigate(`/employees/${id}`);
    } else {
      
      await api.post("api/employees/", employeeData);
      alert("Employee added successfully!");
      navigate("/employees");
    }
  } catch (err) {
    console.error("Failed to submit employee data:", err);
    setError(
      err.response?.data?.email?.[0] ||
      err.response?.data?.detail ||
      "An error occurred. Please check the form data."
    );
  } finally {
    setIsLoading(false);
  }
};

  if (isLoading) {
    return (
      <div
        className="d-flex justify-content-center align-items-center"
        style={{ minHeight: "80vh" }}
      >
        <Spinner animation="border" />
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <Card>
        <Card.Header>
          {isEditing ? "Edit Employee" : "Add New Employee"}
        </Card.Header>
        <Card.Body>
          {error && <Alert variant="danger">{error}</Alert>}
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>First Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    required
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Middle Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="middle_name"
                    value={formData.middle_name}
                    onChange={handleChange}
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Last Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    required
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Email</Form.Label>
                  <Form.Control
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Phone</Form.Label>
                  <Form.Control
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Address</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={3}
                    name="address"
                    value={formData.address}
                    onChange={handleChange}
                    required
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Gender</Form.Label>
                  <Form.Select
                    name="gender"
                    value={formData.gender}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                  </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Department</Form.Label>
                  <Form.Select
                    name="department"
                    value={formData.department}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select Department</option>
                    {departments?.map((dept) => (
                      <option key={dept.id} value={dept.id}>
                        {dept.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Label>Job Title</Form.Label>
                  <Form.Select
                    name="job_title"
                    value={formData.job_title}
                    onChange={handleChange}
                    required
                  >
                    <option value="">Select Job Title</option>
                    {jobTitles.map((job) => (
                      <option key={job.id} value={job.id}>
                        {job.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Label>Status</Form.Label>
                    <Form.Select
                      name="status"
                      value={formData.status}
                      onChange={handleChange}
                    >
                      <option value="pending">Pending</option>
                      <option value="active">Active</option>
                      <option value="notice">On Notice Period</option>
                      <option value="inactive">Inactive</option>
                    </Form.Select>
                  </Form.Group>
              </Col>
            </Row>
            <hr />
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Password</Form.Label>
                  <Form.Control
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required={!isEditing}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Confirm Password</Form.Label>
                  <Form.Control
                    type="password"
                    name="password2"
                    value={formData.password2}
                    onChange={handleChange}
                    required={!isEditing}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Check
                type="checkbox"
                label="Is this an HR employee?"
                name="is_hr"
                checked={formData.is_hr}
                onChange={handleChange}
              />
            </Form.Group>
            <Button variant="primary" type="submit" disabled={isLoading}>
              {isLoading ? (
                <Spinner animation="border" size="sm" />
              ) : isEditing ? (
                "Save Changes"
              ) : (
                "Add Employee"
              )}
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
}

export default AddEmployee;