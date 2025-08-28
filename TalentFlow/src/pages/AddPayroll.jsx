import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom"; // ✅ Import useParams
import useAxios from "../utils/useAxios";
import { Form, Button, Container, Row, Col, Alert } from "react-bootstrap";
// import { format } from 'date-fns';

function AddPayroll() {
    const navigate = useNavigate();
    const { id } = useParams(); // ✅ Get the ID from the URL
    const api = useAxios();
    const [employees, setEmployees] = useState([]);
    const [formData, setFormData] = useState({
        employee: "",
        year: new Date().getFullYear(),
        month: new Date().getMonth() + 1,
        compensation: 0,
        bonus: 0,
        deductions: 0,
        tax: 0,
    });
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [isEditing, setIsEditing] = useState(false); // ✅ Track whether we are editing

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch employees for the dropdown
                const employeesResponse = await api.get('api/employees/');
                setEmployees(employeesResponse.data.results);

                // ✅ Check if an ID exists in the URL
                if (id) {
                    setIsEditing(true);
                    // Fetch the payroll data to be edited
                    const payrollResponse = await api.get(`hr/payroll/${id}/`);
                    const payrollData = payrollResponse.data;
                    setFormData({
                        employee: payrollData.employee?.id || "",
                        year: payrollData.year,
                        month: payrollData.month,
                        compensation: payrollData.compensation,
                        bonus: payrollData.bonus,
                        deductions: payrollData.deductions,
                        tax: payrollData.tax,
                    });
                }
            } catch (error) {
                console.error("Failed to fetch data:", error);
                setError("Failed to fetch data. Please try again.");
            }
        };
        fetchData();
    }, [api, id]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setSuccess("");

        const dataToSend = {
            ...formData,
            employee: parseInt(formData.employee),
            compensation: parseFloat(formData.compensation),
            bonus: parseFloat(formData.bonus),
            deductions: parseFloat(formData.deductions),
            tax: parseFloat(formData.tax),
        };

        try {
            if (isEditing) {
                // ✅ Send a PATCH request for editing
                await api.patch(`hr/payroll/${id}/`, dataToSend);
                setSuccess("Payroll entry updated successfully!");
            } else {
                // ✅ Send a POST request for adding
                await api.post('hr/payroll/', dataToSend);
                setSuccess("Payroll entry added successfully!");
            }

            setTimeout(() => {
                navigate('/payroll');
            }, 2000);
        } catch (error) {
            console.error("Failed to submit payroll:", error.response?.data);
            setError(error.response?.data?.detail || "Failed to submit payroll. Please check the form data.");
        }
    };

    return (
        <Container className="mt-4">
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h4 className="text-primary">{isEditing ? "Edit Payroll" : "Add New Payroll"}</h4> {/* ✅ Change the title dynamically */}
            </div>
            {error && <Alert variant="danger">{error}</Alert>}
            {success && <Alert variant="success">{success}</Alert>}
            <Form onSubmit={handleSubmit}>
                {/* ... (rest of the form fields are the same) ... */}
                <Row className="mb-3">
                    <Col>
                        <Form.Group controlId="employee">
                            <Form.Label>Employee</Form.Label>
                            <Form.Control
                                as="select"
                                name="employee"
                                value={formData.employee}
                                onChange={handleChange}
                                required
                            >
                                <option value="">Select an employee</option>
                                {employees.map((emp) => (
                                    <option key={emp.id} value={emp.id}>
                                        {emp.first_name} {emp.last_name}
                                    </option>
                                ))}
                            </Form.Control>
                        </Form.Group>
                    </Col>
                    <Col>
                        <Form.Group controlId="year">
                            <Form.Label>Year</Form.Label>
                            <Form.Control
                                type="number"
                                name="year"
                                value={formData.year}
                                onChange={handleChange}
                                required
                            />
                        </Form.Group>
                    </Col>
                    <Col>
                        <Form.Group controlId="month">
                            <Form.Label>Month</Form.Label>
                            <Form.Control
                                as="select"
                                name="month"
                                value={formData.month}
                                onChange={handleChange}
                                required
                            >
                                {Array.from({ length: 12 }, (_, i) => (
                                    <option key={i + 1} value={i + 1}>{i + 1}</option>
                                ))}
                            </Form.Control>
                        </Form.Group>
                    </Col>
                </Row>
                <Row className="mb-3">
                    <Col>
                        <Form.Group controlId="compensation">
                            <Form.Label>Compensation</Form.Label>
                            <Form.Control
                                type="number"
                                name="compensation"
                                value={formData.compensation}
                                onChange={handleChange}
                                required
                            />
                        </Form.Group>
                    </Col>
                    <Col>
                        <Form.Group controlId="bonus">
                            <Form.Label>Bonus</Form.Label>
                            <Form.Control
                                type="number"
                                name="bonus"
                                value={formData.bonus}
                                onChange={handleChange}
                            />
                        </Form.Group>
                    </Col>
                </Row>
                <Row className="mb-3">
                    <Col>
                        <Form.Group controlId="deductions">
                            <Form.Label>Deductions</Form.Label>
                            <Form.Control
                                type="number"
                                name="deductions"
                                value={formData.deductions}
                                onChange={handleChange}
                            />
                        </Form.Group>
                    </Col>
                    <Col>
                        <Form.Group controlId="tax">
                            <Form.Label>Tax</Form.Label>
                            <Form.Control
                                type="number"
                                name="tax"
                                value={formData.tax}
                                onChange={handleChange}
                            />
                        </Form.Group>
                    </Col>
                </Row>
                <div className="d-flex justify-content-between">
                    <Button variant="primary" type="submit">
                        {isEditing ? "Save Changes" : "Submit"} {/* ✅ Change the button text dynamically */}
                    </Button>
                    <Button variant="secondary" onClick={() => navigate('/payroll')}>
                        Cancel
                    </Button>
                </div>
            </Form>
        </Container>
    );
}

export default AddPayroll;