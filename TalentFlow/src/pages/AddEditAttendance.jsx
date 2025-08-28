import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import useAxios from "../utils/useAxios";
import { Form, Button, Container, Row, Col, Alert } from "react-bootstrap";
import { format, parseISO } from 'date-fns';
import { formatInTimeZone } from 'date-fns-tz';

function AddEditAttendance() {
    const navigate = useNavigate();
    const { id } = useParams();
    const api = useAxios();
    const [employees, setEmployees] = useState([]);
    const [formData, setFormData] = useState({
        employee: "",
        date: format(new Date(), 'yyyy-MM-dd'),
        check_in: "",
        check_out: "",
    });
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [isEditing, setIsEditing] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const employeesPromise = api.get('api/employees/');
                const attendancePromise = id ? api.get(`attendance/attendance/${id}/`) : Promise.resolve(null);
                const [employeesResponse, attendanceResponse] = await Promise.all([employeesPromise, attendancePromise]);

                setEmployees(employeesResponse.data.results);

                if (attendanceResponse?.data) {
                    setIsEditing(true);
                    const attendanceData = attendanceResponse.data;
                    
                    const formattedCheckIn = attendanceData.check_in ? format(parseISO(attendanceData.check_in), "yyyy-MM-dd'T'HH:mm") : "";
                    const formattedCheckOut = attendanceData.check_out ? format(parseISO(attendanceData.check_out), "yyyy-MM-dd'T'HH:mm") : "";

                    setFormData({
                        employee: String(attendanceData.employee.id),
                        date: attendanceData.date,
                        check_in: formattedCheckIn,
                        check_out: formattedCheckOut,
                    });
                } else {
                    setIsEditing(false);
                    setFormData({
                        employee: "",
                        date: format(new Date(), 'yyyy-MM-dd'),
                        check_in: "",
                        check_out: "",
                    });
                }
            } catch (error) {
                console.error("Failed to fetch data:", error);
                setError("Failed to fetch data. Please try again.");
            } finally {
                setLoading(false);
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
    
        try {
            let submissionData = { ...formData };

            // Get the user's local timezone
            const userTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;

            if (submissionData.check_in) {
                // Format the date for the backend, including the timezone offset
                submissionData.check_in = formatInTimeZone(new Date(submissionData.check_in), userTimeZone, "yyyy-MM-dd'T'HH:mm:ssXXX");
            }
            if (submissionData.check_out) {
                // Do the same for check_out
                submissionData.check_out = formatInTimeZone(new Date(submissionData.check_out), userTimeZone, "yyyy-MM-dd'T'HH:mm:ssXXX");
            }

            if (isEditing) {
                await api.patch(`attendance/attendance/${id}/`, submissionData);
                setSuccess("Attendance record updated successfully!");
            } else {
                await api.post('attendance/attendance/', submissionData);
                setSuccess("Attendance record added successfully!");
            }
    
            setTimeout(() => {
                navigate('/attendance');
            }, 2000);
        } catch (error) {
            console.error("Failed to submit attendance:", error.response?.data);
            if (error.response?.data) {
                const errorKey = Object.keys(error.response.data)[0];
                const errorMessage = error.response.data[errorKey][0];
                setError(`${errorKey}: ${errorMessage}`);
            } else {
                setError("Failed to submit attendance. Please check the form data.");
            }
        }
    };

    return (
        <Container className="mt-4">
            {loading ? (
                <p>Loading...</p>
            ) : (
                <>
                    <h4 className="text-primary mb-3">{isEditing ? "Edit Attendance" : "Add New Attendance"}</h4>
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
                                            <option key={emp.id} value={String(emp.id)}>
                                                {emp.first_name} {emp.last_name}
                                            </option>
                                        ))}
                                    </Form.Control>
                                </Form.Group>
                            </Col>
                            <Col>
                                <Form.Group controlId="date">
                                    <Form.Label>Date</Form.Label>
                                    <Form.Control
                                        type="date"
                                        name="date"
                                        value={formData.date}
                                        onChange={handleChange}
                                        required
                                    />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Row className="mb-3">
                            <Col>
                                <Form.Group controlId="check_in">
                                    <Form.Label>Check-in Time</Form.Label>
                                    <Form.Control
                                        type="datetime-local"
                                        name="check_in"
                                        value={formData.check_in}
                                        onChange={handleChange}
                                    />
                                </Form.Group>
                            </Col>
                            <Col>
                                <Form.Group controlId="check_out">
                                    <Form.Label>Check-out Time</Form.Label>
                                    <Form.Control
                                        type="datetime-local"
                                        name="check_out"
                                        value={formData.check_out}
                                        onChange={handleChange}
                                    />
                                </Form.Group>
                            </Col>
                        </Row>
                        <div className="d-flex justify-content-between">
                            <Button variant="primary" type="submit">
                                {isEditing ? "Save Changes" : "Submit"}
                            </Button>
                            <Button variant="secondary" onClick={() => navigate('/attendance')}>
                                Cancel
                            </Button>
                        </div>
                    </Form>
                </>
            )}
        </Container>
    );
}

export default AddEditAttendance;