import React, { useEffect, useState } from "react";
import Papa from "papaparse";
import "./AttendancePanel.css";

const AttendancePanel = () => {
  const [attendance, setAttendance] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchCSV = async () => {
    try {
      const res = await fetch("/attendance.csv?cachebuster=" + Date.now());
      const csvText = await res.text();

      Papa.parse(csvText, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          setAttendance(results.data);
          setLastUpdated(new Date().toLocaleTimeString());
        },
      });
    } catch (err) {
      console.error("Error fetching CSV:", err);
    }
  };

  useEffect(() => {
    fetchCSV();
    const interval = setInterval(fetchCSV, 500); // refresh every 2 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="attendance-container">
      <div className="attendance-wrapper">
        <h1 className="attendance-title">Attendance Panel</h1>

        <div className="attendance-last-updated">
          Last updated: {lastUpdated || "Loading..."}
        </div>

        <div className="attendance-table-wrapper">
          <table className="attendance-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Student ID</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {attendance.length === 0 ? (
                <tr>
                  <td colSpan="3" className="attendance-empty">
                    No attendance data yet...
                  </td>
                </tr>
              ) : (
                attendance.map((row, idx) => (
                  <tr key={idx}>
                    <td>{row["Name"]}</td>
                    <td>{row["Student ID"]}</td>
                    <td>{row["Timestamp"]}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AttendancePanel;
