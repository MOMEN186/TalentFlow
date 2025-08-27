import { useEffect, useState } from "react";
import Table from "react-bootstrap/Table";
import { useNavigate } from "react-router-dom";
import useAxios from "../utils/useAxios";
import { handleDownload } from "../utils/file_download";
import Paginate from "../components/Paginate";
import { Tabs, Tab } from 'react-bootstrap';
import { FaCheckCircle, FaTimesCircle } from 'react-icons/fa';

function LeaveNote() {
    const navigate = useNavigate();
    const api = useAxios();
    const [leaveNotes, setLeaveNotes] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [activeTab, setActiveTab] = useState("all");

    const getLeaveNotes = async () => {
        setLeaveNotes([]);
        const params = { page: page };

        if (activeTab !== "all") {
            params.status = activeTab;
        }
        console.log('Sending params:', params);
        
        try {
            const response = await api.get('api/leave_notes/', { params: params });
            console.log('Received data:', response.data);
            setLeaveNotes(response.data.results);
            setTotalPages(Math.ceil(response.data.count / 50));
        } catch (error) {
            console.error("Failed to fetch leave notes:", error);
            setLeaveNotes([]);
        }
    };

    useEffect(() => {
        getLeaveNotes();
    }, [page, activeTab]);

    const handleUpdateStatus = async (noteId, newStatus) => {
        const confirmUpdate = window.confirm(
            `Are you sure you want to change the status to '${newStatus}'?`
        );
        if (confirmUpdate) {
            try {
                await api.patch(`http://127.0.0.1:8000/api/leave_notes/${noteId}/`, {
                    status: newStatus
                });
                alert("Leave note status updated successfully!");
                getLeaveNotes();
            } catch (error) {
                console.error("Failed to update leave note status:", error.response?.data);
                alert(`Error: ${error.response?.data?.status || "Unknown error"}`);
            }
        }
    };

    return (
        <div
            className="mt-4"
            style={{
                flex: 1,
                width: "100%",
                padding: "0 16px",
                overflow: "auto",
                minHeight: "100vh",
            }}
        >
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h4 className="text-primary">Leave Notes</h4>
                <div>
                    <button
                        className="btn btn-primary me-2"
                        onClick={() => navigate("/leave_notes/add")}
                    >
                        Add Leave Note
                    </button>
                    <button
                        className="btn btn-success"
                        onClick={() => handleDownload(api, "leave_notes")}
                    >
                        Download Excel
                    </button>
                </div>
            </div>

            <Tabs
                id="leave-notes-tabs"
                activeKey={activeTab}
                onSelect={(k) => {
                    setActiveTab(k);
                    setPage(1);
                }}
                className="mb-3"
            >
                <Tab eventKey="all" title="All" />
                <Tab eventKey="pending" title="Pending" />
                <Tab eventKey="approved" title="Approved" />
                <Tab eventKey="denied" title="Denied" />
            </Tabs>

            <Table striped bordered hover size="sm">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Employee ID</th>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Date</th>
                        <th>Return Date</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {leaveNotes.length > 0 ? (
                        leaveNotes.map((note, idx) => (
                            <tr key={note.id}>
                                <td>{50 * (page - 1) + idx + 1}</td>
                                <td>{note.employee}</td>
                                <td>{note.name}</td>
                                <td>{note.description}</td>
                                <td>{note.date}</td>
                                <td>{note.return_date}</td>
                                <td>{note.status}</td>
                                <td>
                                    <div style={{ display: "flex", gap: "10px" }}>
                                        {note.status === 'pending' && (
                                            <>
                                                <FaCheckCircle
                                                    onClick={() => handleUpdateStatus(note.id, 'approved')}
                                                    style={{ cursor: "pointer", color: "green" }}
                                                    title="Approve"
                                                />
                                                <FaTimesCircle
                                                    onClick={() => handleUpdateStatus(note.id, 'denied')}
                                                    style={{ cursor: "pointer", color: "red" }}
                                                    title="Deny"
                                                />
                                            </>
                                        )}
                                    </div>
                                </td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="8" className="text-center">
                                No leave notes found.
                            </td>
                        </tr>
                    )}
                </tbody>
            </Table>
            <Paginate page={page} totalPages={totalPages} setPage={setPage} />
        </div>
    );
}

export default LeaveNote;