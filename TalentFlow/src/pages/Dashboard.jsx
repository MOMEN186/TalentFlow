import React, { useState, useEffect } from 'react';
import { Card, Row, Col } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import useAxios from '../utils/useAxios';

function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const api = useAxios();

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await api.get('/reports/turnover/');
        setMetrics(response.data);
      } catch (error) {
        console.error('Error fetching metrics:', error);
      }
    };
    fetchMetrics();
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short' 
    });
  };

  return (
    <div style={{
      width: "100%",
      minHeight: "100vh",
      padding: "20px",
      overflow: "hidden"
    }}>
      <h2 className="mb-4">HR Analytics Dashboard</h2>
      
      {/* Summary Cards */}
      <Row className="g-4 mb-4">
        <Col xs={12} sm={6} lg={3}>
          <Card className="shadow-sm h-100">
            <Card.Body className="d-flex flex-column justify-content-center align-items-center">
              <h6 className="text-muted mb-3">Total Hires</h6>
              <h2 className="text-primary mb-0">{metrics?.hires_total || 0}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col xs={12} sm={6} lg={3}>
          <Card className="shadow-sm h-100">
            <Card.Body className="d-flex flex-column justify-content-center align-items-center">
              <h6 className="text-muted mb-3">Total Exits</h6>
              <h2 className="text-danger mb-0">{metrics?.exits_total || 0}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col xs={12} sm={6} lg={3}>
          <Card className="shadow-sm h-100">
            <Card.Body className="d-flex flex-column justify-content-center align-items-center">
              <h6 className="text-muted mb-3">Current Headcount</h6>
              <h2 className="text-success mb-0">{metrics?.headcount_end || 0}</h2>
            </Card.Body>
          </Card>
        </Col>
        <Col xs={12} sm={6} lg={3}>
          <Card className="shadow-sm h-100">
            <Card.Body className="d-flex flex-column justify-content-center align-items-center">
              <h6 className="text-muted mb-3">Attrition Rate</h6>
              <h2 className="text-warning mb-0">{metrics?.attrition_rate_percent || 0}%</h2>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Chart Section */}
      <Card className="shadow-sm mb-4">
        <Card.Body>
          <h5 className="mb-4">Monthly Hires vs Exits</h5>
          <div style={{ width: '100%', height: '400px' }}>
            <ResponsiveContainer>
              <BarChart
                data={metrics?.hires_by_month?.map(item => ({
                  month: formatDate(item.month),
                  hires: item.count,
                  exits: metrics?.exits_by_month?.find(
                    exit => exit.month === item.month
                  )?.count || 0
                })) || []}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="hires" fill="#0d6efd" name="Hires" />
                <Bar dataKey="exits" fill="#dc3545" name="Exits" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card.Body>
      </Card>

      {/* Date Range Info */}
      <Card className="shadow-sm">
        <Card.Body>
          <h5 className="mb-3">Report Period</h5>
          <div className="d-flex gap-4">
            <div>
              <span className="text-muted">From:</span>
              <br />
              {metrics?.date_range?.start && formatDate(metrics.date_range.start)}
            </div>
            <div>
              <span className="text-muted">To:</span>
              <br />
              {metrics?.date_range?.end && formatDate(metrics.date_range.end)}
            </div>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
}

export default Dashboard;