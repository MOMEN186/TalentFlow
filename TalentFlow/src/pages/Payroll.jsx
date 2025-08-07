import React, { useEffect, useState } from "react";
import useAxios from "../utils/useAxios";
import Table from "react-bootstrap/Table";
import { handleDownload } from "../utils/file_download";
function Payroll() {
  const [payroll, setPayroll] = useState([]);
  const api = useAxios();

  useEffect(() => {
    const get = async () => {
      const res = await api("/payroll/");
      console.log(res.data)
      setPayroll(res.data);
    };
    get();
  }, []);

  useEffect(()=>{console.log(payroll);},[payroll])

  return (
    <div
      className="mt-4"
      style={{
        flex: 1,
        width: "100%",
        padding: "0 16px", // Add horizontal padding
        overflow: "auto",
        minHeight: "100vh",
      }}
    >
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4 className="text-primary">PayRoll </h4>
        <button className="btn btn-success" onClick={()=>handleDownload(api,"payroll")}>
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
            <th>#</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Compensation</th>
            <th>Bonus</th>
            <th>Tax</th>
            <th>Deductions</th>
            <th>Gross Pay</th>
            <th>Net Pay</th>
          </tr>
        </thead>
        <tbody>
          {payroll&& payroll.length > 0 &&
payroll.map((item, index) => (
            <tr key={item.id}>
              <td>{index + 1}</td>
              <td>{item.first_name}</td>
              <td>{item.last_name}</td>
              <td>{item.compensation}</td>
              <td>{item.bonus}</td>
              <td>{item.tax}</td>
              <td>{item.deductions}</td>
              <td>{item.gross_pay}</td>
              <td>{item.net_pay}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}

export default Payroll;
