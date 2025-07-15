import React, { useState, useRef } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [pdfUrl, setPdfUrl] = useState(null);
  const inputRef = useRef();
  const [meetings, setMeetings] = useState([]);
  const [briefData, setBriefData] = useState(null);
  const [showMeetings, setShowMeetings] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setStatus("");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setStatus("Generating brief and scheduling meetings...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/brief-with-meetings", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Brief generation failed");

      const data = await response.json();
      // Set the meeting data
      setMeetings(data.meetings || []);
      setBriefData(data);

      const pdfResponse = await fetch(`http://127.0.0.1:8000/download-pdf/${data.pdf_path}`);
      if (pdfResponse.ok) {
        const pdfBlob = await pdfResponse.blob();
        const url = window.URL.createObjectURL(pdfBlob);
        setPdfUrl(url);
      }

      // setPdfUrl(url);
      setStatus("Brief generated!");
    } catch (err) {
      console.error(err);
      setStatus("Error: " + err.message);
    }
  };

  const formatDateTime = (dateString) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="container">
      <div className="header">
        <img src="/infosys-logo.png" alt="Infosys" className="logo" />
        <div className="signin">👤 Login/Sign In</div>
      </div>

      <div className="titles">
        <h1 className="title">AutoBrief</h1>
        <p className="subtitle">Turn your media into concise creative briefs.</p>
      </div>

      <form
        className="dropzone"
        onClick={() => inputRef.current.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        <img src="/upload-blue.png" alt="upload" className="upload-icon" />
        <p>
          <strong>
            Drop your images here, or <span className="browse">browse</span>
          </strong>
        </p>
        <p className="hint">
          Supports TXT, PDF, CSV, XLSX, PNG, JPG, MP3, MP4
        </p>
        <input
          type="file"
          onChange={handleFileChange}
          ref={inputRef}
          hidden
          required
        />
        {status && <div className="status">{status}</div>}
      </form>

      {file && (
        <div className="file-preview">
          <div className="file-info">
            <img src="/file-icon.png" alt="file" className="file-icon" />
            <span className="file-name">{file.name}</span>
          </div>
          <button
            type="button"
            className="close-btn"
            onClick={() => {
              setFile(null);
              setPdfUrl(null);
              setMeetings([]);
              setBriefData(null);
              setStatus("");
              setShowMeetings(false);
            }}
          >
            ×
          </button>
        </div>
      )}

      <div className="buttons">
        {file && (
          <button onClick={handleUpload} className="generate-btn">
            Generate Brief
          </button>
        )}

        {pdfUrl && (
          <div className="download-section">
            <a href={pdfUrl} download="brief_output.pdf" className="download-btn">
              Download Brief PDF
            </a>
            {meetings.length > 0 && (
              <button 
                onClick={() => setShowMeetings(!showMeetings)} 
                className="meetings-btn"
                style={{
                  marginLeft: '10px',
                  padding: '10px 20px',
                  backgroundColor: '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer'
                }}
              >
                {showMeetings ? 'Hide' : 'Show'} Meetings ({meetings.length})
              </button>
            )}
          </div>
        )}
      </div>
      {/* Meetings Display */}
      {showMeetings && meetings.length > 0 && (
        <div className="meetings-section" style={{
          marginTop: '30px',
          padding: '20px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px',
          border: '1px solid #dee2e6'
        }}>
          <h3 style={{ color: '#343a40', marginBottom: '20px' }}>
            📅 Scheduled Meetings
          </h3>
          
          {meetings.map((meeting, index) => (
            <div key={index} style={{
              backgroundColor: 'white',
              border: '1px solid #dee2e6',
              borderRadius: '6px',
              padding: '15px',
              marginBottom: '15px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '10px'
              }}>
                <h4 style={{ 
                  margin: 0, 
                  color: '#007bff',
                  fontSize: '16px'
                }}>
                  {meeting.title}
                </h4>
                <span style={{
                  backgroundColor: meeting.priority === 'high' ? '#dc3545' : 
                                 meeting.priority === 'medium' ? '#ffc107' : '#28a745',
                  color: meeting.priority === 'medium' ? '#000' : '#fff',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  fontSize: '12px',
                  fontWeight: 'bold'
                }}>
                  {meeting.priority?.toUpperCase()}
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <p style={{ margin: '5px 0', fontSize: '14px' }}>
                    <strong>📅 Time:</strong> {formatDateTime(meeting.suggested_time)}
                  </p>
                  <p style={{ margin: '5px 0', fontSize: '14px' }}>
                    <strong>⏱️ Duration:</strong> {meeting.duration_minutes} minutes
                  </p>
                  <p style={{ margin: '5px 0', fontSize: '14px' }}>
                    <strong>🎯 Type:</strong> {meeting.meeting_type}
                  </p>
                </div>

                <div>
                  <p style={{ margin: '5px 0', fontSize: '14px' }}>
                    <strong>👥 Attendees:</strong>
                  </p>
                  <ul style={{ margin: '5px 0', paddingLeft: '20px', fontSize: '13px' }}>
                    {meeting.attendee_names?.map((name, i) => (
                      <li key={i}>
                        {name} - <em>{meeting.attendee_roles?.[i]}</em>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {meeting.agenda && (
                <div style={{ marginTop: '10px' }}>
                  <p style={{ margin: '5px 0', fontSize: '14px' }}>
                    <strong>📋 Agenda:</strong>
                  </p>
                  <div style={{
                    backgroundColor: '#f8f9fa',
                    padding: '10px',
                    borderRadius: '4px',
                    fontSize: '13px',
                    whiteSpace: 'pre-line'
                  }}>
                    {meeting.agenda}
                  </div>
                </div>
              )}

              {meeting.teams_link && (
                <div style={{ marginTop: '10px' }}>
                  <a 
                    href={meeting.teams_link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    style={{
                      display: 'inline-block',
                      backgroundColor: '#6264a7',
                      color: 'white',
                      padding: '8px 15px',
                      textDecoration: 'none',
                      borderRadius: '4px',
                      fontSize: '13px'
                    }}
                  >
                    💻 Join Teams Meeting
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Brief Summary */}
      {briefData && (
        <div className="brief-summary" style={{
          marginTop: '20px',
          padding: '15px',
          backgroundColor: '#e3f2fd',
          borderRadius: '6px',
          border: '1px solid #2196f3'
        }}>
          <h4 style={{ margin: '0 0 10px 0', color: '#1976d2' }}>
            📊 Brief Summary
          </h4>
          <p style={{ margin: '5px 0', fontSize: '14px' }}>
            <strong>File processed:</strong> {briefData.file_info?.filename}
          </p>
          <p style={{ margin: '5px 0', fontSize: '14px' }}>
            <strong>Team members involved:</strong> {briefData.team_used}
          </p>
          <p style={{ margin: '5px 0', fontSize: '14px' }}>
            <strong>Meetings scheduled:</strong> {meetings.length}
          </p>
        </div>
      )}
    </div>
  );
}

export default App;