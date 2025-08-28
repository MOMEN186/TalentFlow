import React, { useEffect, useState } from "react";
import Table from "react-bootstrap/Table";
import { useNavigate } from "react-router-dom";
import useAxios from "../utils/useAxios";
import { handleDownload } from "../utils/file_download";
import Paginate from "../components/Paginate";
import { Button, Tabs, Tab } from 'react-bootstrap'; // ✅ استيراد Tabs و Tab
import { FaEdit, FaUndo } from "react-icons/fa";
import { RiDeleteBin6Line } from "react-icons/ri";


function Attendance() {
  const navigate = useNavigate();
  const api = useAxios();
  const [activeAttendance, setActiveAttendance] = useState([]); // ✅ سجلات الحضور النشطة
  const [archivedAttendance, setArchivedAttendance] = useState([]); // ✅ سجلات الحضور المؤرشفة
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [activeTab, setActiveTab] = useState('active'); // ✅ حالة التبويب الحالي ('active' أو 'archived')

  // ✅ دالة لجلب البيانات من الواجهة الخلفية وتقسيمها
  const getAttendance = async () => {
    try {
      // ✅ تعديل مسار API الصحيح
      const res = await api.get(`attendance/attendance/?page=${page}`);
      const allData = res.data.results;
      
      // ✅ عند الجلب، كل السجلات تُعتبر نشطة في البداية. 
      // سنُعيد تعيين السجلات المؤرشفة في كل مرة لجلب البيانات "الجديدة".
      setActiveAttendance(allData);
      setArchivedAttendance([]); // التأكد من أن الأرشيف يبدأ فارغاً عند كل جلب

      setTotalPages(Math.ceil(res.data.count / 50));
    } catch (error) {
      console.error("Failed to fetch attendance data:", error);
      setActiveAttendance([]);
      setArchivedAttendance([]);
    }
  };

  // ✅ دالة للحذف الناعم (في الواجهة الأمامية فقط)
  const handleSoftDelete = (id) => {
    const confirmDelete = window.confirm("Are you sure you want to delete this attendance entry?");
    if (confirmDelete) {
      const itemToArchive = activeAttendance.find(item => item.id === id);
      if (itemToArchive) {
        setActiveAttendance(prevActive => prevActive.filter(item => item.id !== id));
        setArchivedAttendance(prevArchived => [...prevArchived, itemToArchive]);
      }
    }
  };
  
  // ✅ دالة لاستعادة السجل (من الأرشيف إلى النشط)
  const handleRestore = (id) => {
      const confirmRestore = window.confirm("Are you sure you want to restore this attendance entry?");
      if(confirmRestore){
          const itemToRestore = archivedAttendance.find(item => item.id === id);
          if(itemToRestore){
              setArchivedAttendance(prevArchived => prevArchived.filter(item => item.id !== id));
              setActiveAttendance(prevActive => [...prevActive, itemToRestore]);
          }
      }
  };

  useEffect(() => {
    getAttendance();
  }, [page, api]); // عند تغيير الصفحة أو الـ API، أعد جلب البيانات

  // ✅ تحديد البيانات التي سيتم عرضها بناءً على التبويب النشط
  const currentData = activeTab === 'active' ? activeAttendance : archivedAttendance;

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
        <h4 className="text-primary">Attendance</h4>
        <div>
          {/* ✅ زر لإضافة سجل حضور جديد */}
          <button
            className="btn btn-primary me-2"
            onClick={() => navigate("/attendance/add")}
          >
            Add Attendance
          </button>
          {/* زر لتنزيل ملف Excel */}
          <button
            className="btn btn-success"
            onClick={() => handleDownload(api, "attendance")}
          >
            Download Excel
          </button>
        </div>
      </div>
      
      {/* ✅ مكون التبويبات Tabs */}
      <Tabs activeKey={activeTab} onSelect={(k) => {setActiveTab(k); setPage(1);}} className="mb-3">
          <Tab eventKey="active" title="Active Records" />
          <Tab eventKey="archived" title="Archived Records" />
      </Tabs>

      <Table striped bordered hover size="sm">
        <thead>
          <tr>
            <th style={{ width: "4%" }}>#</th>
            <th style={{ width: "10%" }}>First Name</th>
            <th style={{ width: "10%" }}>Last Name</th>
            <th style={{ width: "10%" }}>Middle Name</th>
            <th style={{ width: "12%" }}>Department</th>
            <th style={{ width: "12%" }}>Job Title</th>
            <th style={{ width: "12%" }}>Date</th>
            <th style={{ width: "12%" }}>Check In</th>
            <th style={{ width: "12%" }}>Check Out</th>
            <th style={{ width: "12%" }}>Late (min)</th>
            <th style={{ width: "12%" }}>Overtime (min)</th>
            <th style={{ width: "10%" }}>Actions</th></tr>
        </thead>
        <tbody>
          {currentData && currentData.length > 0 ? (
            currentData.map((item, index) => (
              <tr 
                key={item.id} 
                // ✅ تعديل مسار التنقل ليأخذ employee.id
                onClick={() => navigate(`/employees/${item.employee.id}`)}
                style={{ cursor: "pointer" }}
              >
                <td>{50 * (page - 1) + index + 1}</td>
                <td>{item.employee?.first_name || 'N/A'}</td>
                <td>{item.employee?.last_name || 'N/A'}</td>
                <td>{item.employee?.middle_name || 'N/A'}</td>
                <td>{item.employee?.department || 'N/A'}</td>
                <td>{item.employee?.job_title || 'N/A'}</td>
                <td>{item.date}</td>
                {/* ✅ عرض الوقتين بشكل محلي إذا كانا موجودين */}
                <td>{item.check_in ? new Date(item.check_in).toLocaleString() : 'N/A'}</td>
                <td>{item.check_out ? new Date(item.check_out).toLocaleString() : 'N/A'}</td>
                <td>{item.late_minutes}</td>
                <td>{item.overtime_minutes}</td>
                <td>
                    <div className="d-flex" style={{ gap: "10px" }}>
                        <FaEdit
                                onClick={(e) => { e.stopPropagation(); navigate(`/attendance/edit/${item.id}`); }}
                                style={{ cursor: "pointer", color: "blue", opacity: activeTab === 'archived' ? 0.5 : 1 }}
                        />
                        {activeTab === 'active' ? (
                                // أيقونة الحذف باللون الأحمر
                                <RiDeleteBin6Line
                                    onClick={(e) => { e.stopPropagation(); handleSoftDelete(item.id); }}
                                    style={{ cursor: "pointer", color: "red" }}
                                />
                        ) : (
                                // أيقونة الاستعادة باللون الأخضر
                                <FaUndo
                                    onClick={(e) => { e.stopPropagation(); handleRestore(item.id); }}
                                    style={{ cursor: "pointer", color: "green" }}
                                />
                        )}
                    </div>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="12" className="text-center">
                {activeTab === "active" ? "No active attendance records found." : "No archived attendance records found."}
              </td>
            </tr>
          )}
        </tbody>
      </Table>
      <Paginate totalPages={totalPages} page={page} setPage={setPage} />
    </div>
  );
}

export default Attendance;