import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import useAxios from "../utils/useAxios";
import { Form, Button, Container, Row, Col, Alert } from "react-bootstrap";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { format } from 'date-fns';

function AddLeaveNote() {
    const navigate = useNavigate();
    const api = useAxios();
    const [employees, setEmployees] = useState([]);
    const [formData, setFormData] = useState({
        employee: "",
        date: null,
        return_date: null,
        description: "",
    });
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    useEffect(() => {
        const fetchEmployees = async () => {
            try {
                const response = await api.get('api/employees/');
                setEmployees(response.data.results); // Assuming your employees endpoint is paginated
            } catch (error) {
                console.error("Failed to fetch employees:", error);
            }
        };
        fetchEmployees();
    }, [api]);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleDateChange = (date, fieldName) => {
        setFormData({ ...formData, [fieldName]: date });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setSuccess("");

        const dataToSend = {
            ...formData,
            date: formData.date ? format(formData.date, 'yyyy-MM-dd') : null,
            return_date: formData.return_date ? format(formData.return_date, 'yyyy-MM-dd') : null,
        };

        try {
            await api.post('api/leave_notes/', dataToSend);
            setSuccess("Leave note added successfully!");
            setTimeout(() => {
                navigate('/leave_note');
            }, 2000);
        } catch (error) {
            console.error("Failed to add leave note:", error.response?.data);
            setError(error.response?.data?.detail || "Failed to add leave note. Please check the form data.");
        }
    };

    return (
        <Container className="mt-4">
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h4 className="text-primary">Add New Leave Note</h4>
            </div>
            {error && <Alert variant="danger">{error}</Alert>}
            {success && <Alert variant="success">{success}</Alert>}
            <Form onSubmit={handleSubmit}>
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
                        <Form.Group controlId="date">
                            <Form.Label>Start Date</Form.Label>
                            <DatePicker
                                selected={formData.date}
                                onChange={(date) => handleDateChange(date, "date")}
                                dateFormat="yyyy-MM-dd"
                                className="form-control"
                                required
                            />
                        </Form.Group>
                    </Col>
                </Row>
                <Row className="mb-3">
                    <Col>
                        <Form.Group controlId="return_date">
                            <Form.Label>Return Date</Form.Label>
                            <DatePicker
                                selected={formData.return_date}
                                onChange={(date) => handleDateChange(date, "return_date")}
                                dateFormat="yyyy-MM-dd"
                                className="form-control"
                                required
                            />
                        </Form.Group>
                    </Col>
                </Row>
                <Form.Group controlId="description" className="mb-3">
                    <Form.Label>Description / Reason</Form.Label>
                    <Form.Control
                        as="textarea"
                        rows={3}
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        required
                    />
                </Form.Group>
                <div className="d-flex justify-content-between">
                    <Button variant="primary" type="submit">
                        Submit
                    </Button>
                    <Button variant="secondary" onClick={() => navigate('/leave_notes')}>
                        Cancel
                    </Button>
                </div>
            </Form>
        </Container>
    );
}

export default AddLeaveNote;