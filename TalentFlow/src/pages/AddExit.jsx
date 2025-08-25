

import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import useAxios from "../utils/useAxios";

function AddExit() {
  const { employeeId } = useParams();
  const navigate = useNavigate();
  const api = useAxios();
  const [employee, setEmployee] = useState(null);
  const [formData, setFormData] = useState({
    exit_date: "",
    reason: "",
    notes: "",
    exit_type: "voluntary", 
    final_settlement_amount: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
   
    const fetchEmployee = async () => {
      try {
        const response = await api.get(`/api/employees/${employeeId}/`);
        setEmployee(response.data.employee);
      } catch (err) {
        console.error("Failed to fetch employee details:", err);
        navigate('/employees'); 
      }
    };
    fetchEmployee();
  }, [employeeId, api, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const dataToSend = {
        ...formData,
        employee_id: employeeId, 
      };
      
      
      await api.post("/api/exits/", dataToSend);
      alert("Employee exit process completed successfully!");
      navigate("/employees");
    } catch (err) {
      console.error("Failed to add exit record:", err.response?.data);
      setError(
        err.response?.data?.exit_date?.[0] ||
        err.response?.data?.reason?.[0] ||
        err.response?.data?.detail ||
        "An error occurred. Please check the form data."
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (!employee) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container mt-4">
      <h4 className="text-danger">Exit Process for {employee.first_name} {employee.last_name}</h4>
      {error && <div className="alert alert-danger">{error}</div>}
      <form onSubmit={handleSubmit}>
        
        <div className="mb-3">
          <label className="form-label">Exit Date</label>
          <input
            type="date"
            className="form-control"
            name="exit_date"
            value={formData.exit_date}
            onChange={handleChange}
            required
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Exit Type</label>
          <select
            className="form-control"
            name="exit_type"
            value={formData.exit_type}
            onChange={handleChange}
            required
          >
            <option value="voluntary">Voluntary</option>
            <option value="involuntary">Involuntary</option>
            <option value="end_of_contract">End of contract</option>
          </select>
        </div>
        <div className="mb-3">
          <label className="form-label">Reason</label>
          <input
            type="text"
            className="form-control"
            name="reason"
            value={formData.reason}
            onChange={handleChange}
            required
          />
        </div>
        <div className="mb-3">
          <label className="form-label">Notes</label>
          <textarea
            className="form-control"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
          ></textarea>
        </div>
        <div className="mb-3">
          <label className="form-label">Final Settlement Amount</label>
          <input
            type="number"
            className="form-control"
            name="final_settlement_amount"
            value={formData.final_settlement_amount}
            onChange={handleChange}
            step="0.01"
          />
        </div>
        <button type="submit" className="btn btn-danger me-2" disabled={isLoading}>
          {isLoading ? "Processing..." : "Complete Exit"}
        </button>
        <button type="button" className="btn btn-secondary" onClick={() => navigate(-1)}>
          Cancel
        </button>
      </form>
    </div>
  );
}

export default AddExit;