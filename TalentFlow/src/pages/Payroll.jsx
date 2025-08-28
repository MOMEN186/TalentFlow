import React, { useEffect, useState } from "react";
import useAxios from "../utils/useAxios";
import Table from "react-bootstrap/Table";
import { handleDownload } from "../utils/file_download";
import Paginate from "../components/Paginate";
import { useNavigate } from "react-router-dom";
import { Tabs, Tab, Button } from 'react-bootstrap'; // ✅ Import Tabs and Tab
import { FaEdit, FaTrashAlt } from "react-icons/fa";
import { FaUndo } from "react-icons/fa";

function Payroll() {
  const navigate = useNavigate();
  const api = useAxios();
  const [activePayroll, setActivePayroll] = useState([]); // ✅ البيانات النشطة
  const [archivedPayroll, setArchivedPayroll] = useState([]); // ✅ البيانات المؤرشفة
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [activeTab, setActiveTab] = useState("active"); // ✅ حالة التبويب الحالي

  const getPayroll = async () => {
    try {
      // ✅ جلب كل البيانات
      const res = await api.get(`hr/payroll/?page=${page}`);
      const allData = res.data.results;

      // ✅ تقسيم البيانات إلى نشطة ومؤرشفة بناءً على حالة وهمية
      // هنا يمكنكِ وضع منطق مؤقت لتحديد ما هو "محذوف"
      // مثلاً، سنستخدم قيمة سالبة للمرتب كعلامة للحذف
     
      
      setActivePayroll(allData);
      setArchivedPayroll([]);
      setTotalPages(Math.ceil(res.data.count / 50));
    } catch (error) {
      console.error("Failed to fetch payroll data:", error);
    }
  };

  const handleSoftDelete = (id) => {
        const confirmDelete = window.confirm("Are you sure you want to archive this payroll entry?");
        if (confirmDelete) {
            const itemToArchive = activePayroll.find(item => item.id === id);
            if (itemToArchive) {
                // ✅ نقل العنصر من القائمة النشطة إلى الأرشيف
                setActivePayroll(prevActive => prevActive.filter(item => item.id !== id));
                setArchivedPayroll(prevArchived => [...prevArchived, itemToArchive]);
                alert("Payroll entry archived successfully!");
            }
        }
    };

  const handleRestore = (id) => {
        const confirmRestore = window.confirm("Are you sure you want to restore this payroll entry?");
        if (confirmRestore) {
            const itemToRestore = archivedPayroll.find(item => item.id === id);
            if (itemToRestore) {
                // ✅ نقل العنصر من الأرشيف إلى القائمة النشطة
                setArchivedPayroll(prevArchived => prevArchived.filter(item => item.id !== id));
                setActivePayroll(prevActive => [...prevActive, itemToRestore]);
                alert("Payroll entry restored successfully!");
            }
        }
    };

  useEffect(() => {
    getPayroll();
  }, [page, api]);

  const currentData = activeTab === "active" ? activePayroll : archivedPayroll;

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
        <h4 className="text-primary">Payroll</h4>
        <div>
          <button
            className="btn btn-primary me-2"
            onClick={() => navigate("/payroll/add")}
          >
            Add Payroll
          </button>
          <button
            className="btn btn-success"
            onClick={() => handleDownload(api, "payroll")}
          >
            Download Excel
          </button>
        </div>
      </div>

      {/* ✅ إضافة التبويبات */}
      <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k)} className="mb-3">
        <Tab eventKey="active" title="Active" />
        <Tab eventKey="archived" title="Archived" />
      </Tabs>

      <Table striped bordered hover size="sm">
        <thead>
          <tr>
            <th>#</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Compensation</th>
            <th>Bonus</th>
            <th>Tax</th>
            <th>Deductions</th>
            <th>Gross Pay</th>
            <th>Net Pay</th>
            <th>Actions</th> {/* ✅ عمود الإجراءات */}
          </tr>
        </thead>
        <tbody>
          {currentData && currentData.length > 0 ? (
            currentData.map((item, index) => (
              <tr key={item.id}>
                <td>{50 * (page - 1) + index + 1}</td>
                <td>{item.employee?.first_name || 'N/A'}</td>
                <td>{item.employee?.last_name || 'N/A'}</td>
                <td>{item.compensation}</td>
                <td>{item.bonus}</td>
                <td>{item.tax}</td>
                <td>{item.deductions}</td>
                <td>{item.gross_pay}</td>
                <td>{item.net_pay}</td>
                <td>
                  <div className="d-flex" style={{ gap: "10px" }}>
                    <FaEdit
                      onClick={() => navigate(`/payroll/edit/${item.id}`)}
                      style={{ cursor: "pointer", color: "blue", opacity: activeTab === 'archived' ? 0.5 : 1 }}
                    />
                    {activeTab === 'active' ? (
                      // أيقونة الحذف باللون الأحمر
                      <FaTrashAlt
                          onClick={() => handleSoftDelete(item.id)}
                          style={{ cursor: "pointer", color: "red" }}
                      />
                    ) : (
                      // أيقونة الاستعادة باللون الأخضر
                      <FaUndo
                          onClick={() => handleRestore(item.id)}
                          style={{ cursor: "pointer", color: "green" }}
                      />
                    )}
                  </div>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="10" className="text-center">
                {activeTab === "active" ? "No active payroll records found." : "No archived payroll records found."}
              </td>
            </tr>
          )}
        </tbody>
      </Table>
      <Paginate totalPages={totalPages} page={page} setPage={setPage} />
    </div>
  );
}

export default Payroll;