import React, { useEffect, useState } from 'react';
import useAxios from "../utils/useAxios";
import Table from "react-bootstrap/Table";
import { handleDownload } from '../utils/file_download';
import Paginate from '../components/Paginate';
// import { useParams } from 'react-router-dom';
function LeaveNote() {
  const [leaveNotes, setLeaveNotes] = useState([]);
  const api = useAxios();
  const [page, setPage] = useState(1);

  const [totalPages, setTotalPages] = useState(1);

  // 1) Fetch JSON for display
  useEffect(() => {
    (async () => {
      try {
        const res = await api(`api/leave_notes/?page=${page}`);
        console.log(res.data);
        setLeaveNotes(res.data.results);
      setTotalPages(Math.ceil(res.data.count / 50));
      } catch (err) {
        console.error("Failed to load leave notes:", err);
      }
    })();
  }, [page]);

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
        <button
          className="btn btn-success"
          onClick={() => handleDownload(api, "leave_notes")}
        >
          Download Excel
        </button>
      </div>

      <Table
        striped
        bordered
        hover
        size="sm"
        style={{
          width: "100%",
          tableLayout: "fixed",
          borderCollapse: "collapse",
        }}
      >
        <thead>
          <tr>
            <th style={{ width: "15%" }}>Name</th>
            <th style={{ width: "40%" }}>Description</th>
            <th style={{ width: "15%" }}>Date</th>
            <th style={{ width: "15%" }}>Return Date</th>
            <th style={{ width: "10%" }}>Employee ID</th>
          </tr>
        </thead>
        <tbody>
          {leaveNotes?.length === 0 ? (
            <tr>
              <td colSpan={5} className="text-center">
                No leave notes found
              </td>
            </tr>
          ) : (
            leaveNotes &&
            leaveNotes.length&&
            leaveNotes.map((note) => (
              <tr key={note.id}>
                <td>{note.name}</td>
                <td>{note.description}</td>
                <td>{note.date}</td>
                <td>{note.return_date}</td>
                <td>{note.employee}</td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
      <Paginate totalPages={totalPages} page={page} setPage={setPage} />
    </div>
  );
}

export default LeaveNote;
