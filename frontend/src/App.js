import React, { useState, useRef } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState([]);
  const [status, setStatus] = useState("");
  const [pdfUrl, setPdfUrl] = useState(null);
  const [language, setLanguage] = useState("English");
  const inputRef = useRef();
  const [meetings, setMeetings] = useState([]);
  const [actions, setActions] = useState([]);
  const [briefData, setBriefData] = useState(null);
  const [showMeetings, setShowMeetings] = useState(false);

  const handleFileChange = (e) => {
    setFile([...file, ...e.target.files]);
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

    setStatus("Generating brief...");

    const formData = new FormData();
    file.forEach((f) => formData.append("files", f));
    formData.append("language", language);


    try {
      const response = await fetch("http://127.0.0.1:8000/brief-with-meetings", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Brief generation failed");

      const data = await response.json();
      // Set the meeting data
      setMeetings(data.meetings || []);
      setActions(data.actions || []);
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
        <div className="signin">
          <img src="/user-icon.png" alt="User Icon" className="user-icon" />
          Login / Sign In
        </div>
      </div>

      <div className="titles">
        <h1 className="title">AutoBrief</h1>
        <p className="subtitle">Turn your media into concise creative briefs.</p>
      </div>

      <div className="language-selector">
        <label htmlFor="language">Brief Language:</label>
        <select
          id="language"
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
        >
          <option value="English">English</option>
          <option value="Spanish">Spanish</option>
          <option value="French">French</option>
          <option value="German">German</option>
          <option value="Hindi">Hindi</option>
          <option value="Chinese">Chinese</option>
        </select>
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
          multiple
        />
        {status && <div className="status">{status}</div>}
      </form>

      {file.length > 0 && file.map((f, idx) => (
        <div key={idx} className="file-preview">
          <div className="file-info">
            <img src="/file-icon.png" alt="file" className="file-icon" />
            <span className="file-name">{f.name}</span>
          </div>
          <button
            type="button"
            className="close-btn"
            onClick={() => {
              const updatedFiles = [...file];
              updatedFiles.splice(idx, 1);
              setFile(updatedFiles);

              if (updatedFiles.length === 0) {
                setPdfUrl(null);
                setMeetings([]);
                setBriefData(null);
                setStatus("");
                setShowMeetings(false);
                setActions([]);
              }
            }}
          >
            ×
          </button>
        </div>
      ))}


      <div className="buttons">
        {!pdfUrl && file && (
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
              >
                {showMeetings ? 'Hide' : 'Show'} Details ({meetings.length})
              </button>
            )}
          </div>
        )}
      </div>
      <div style={{ 
        display: 'flex', 
        gap: '15px',           // Space between items
        alignItems: 'center'   // Vertically center
      }}>
        {/* Meetings Display */}
        {showMeetings && meetings.length > 0 && (
          <div className="meetings-section" style={{
            marginTop: '30px',
            padding: '20px',
            paddingLeft: '18px',
            paddingRight: '18px',
            backgroundColor: '#f8f9fa',
            borderRadius: '8px',
            border: '1px solid #dee2e6'
          }}>
            <h3 style={{ color: '#343a40', marginBottom: '20px', textAlign: 'center' }}>
              Scheduled Meetings
            </h3>
            
            {meetings.map((meeting, index) => (
              <div key={index} style={{
                backgroundColor: 'white',
                border: '1px solid #dee2e6',
                borderRadius: '6px',
                paddingLeft: '100px',
                paddingRight: '100px',
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
                      <strong>Time:</strong> {formatDateTime(meeting.suggested_time)}
                    </p>
                    <p style={{ margin: '5px 0', fontSize: '14px' }}>
                      <strong>Duration:</strong> {meeting.duration_minutes} minutes
                    </p>
                    <p style={{ margin: '5px 0', fontSize: '14px' }}>
                      <strong>Type:</strong> {meeting.meeting_type}
                    </p>
                  </div>

                  <div>
                    <p style={{ margin: '5px 0', fontSize: '14px' }}>
                      <strong>Attendees:</strong>
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
                      <strong>Agenda:</strong>
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
                  <div style={{ marginTop: '10px', textAlign: 'center' }}>
                    <a 
                      href={meeting.teams_link} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{
                        display: 'inline-block',
                        backgroundColor: '#007cc3',
                        color: 'white',
                        padding: '8px 15px',
                        textDecoration: 'none',
                        borderRadius: '4px',
                        fontSize: '13px'
                      }}
                    >
                      Join Teams Meeting
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
       <div style={{ 
        display: 'flex', 
        gap: '15px',           // Space between items
        alignItems: 'center'   // Vertically center
      }}>
        {/* Actions Display */}
        {showMeetings && actions.length > 0 && (
          <div className="actions-section" style={{
            marginTop: '30px',
            marginBottom: '30px',
            padding: '20px',
            backgroundColor: '#f8f9fa',
            borderRadius: '8px',
            border: '1px solid #dee2e6'
          }}>
            <h3 style={{ color: '#343a40', marginBottom: '20px', textAlign: 'center' }}>
              Actionable Items ({actions.length})
            </h3>
            
            {actions.map((action, index) => (
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
                  alignItems: 'flex-start',
                  marginBottom: '10px'
                }}>
                  <h4 style={{ 
                    margin: 0, 
                    color: '#007bff',
                    fontSize: '16px',
                    flex: 1,
                    paddingRight: '10px'
                  }}>
                    {action.task}
                  </h4>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <span style={{
                      backgroundColor: action.priority === 'high' ? '#dc3545' : 
                                    action.priority === 'medium' ? '#ffc107' : '#28a745',
                      color: action.priority === 'medium' ? '#000' : '#fff',
                      padding: '3px 8px',
                      borderRadius: '12px',
                      fontSize: '11px',
                      fontWeight: 'bold'
                    }}>
                      {action.priority?.toUpperCase()}
                    </span>
                    <span style={{
                      backgroundColor: '#6c757d',
                      color: '#fff',
                      padding: '3px 8px',
                      borderRadius: '12px',
                      fontSize: '11px',
                      fontWeight: 'bold'
                    }}>
                      {action.category?.toUpperCase()}
                    </span>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                  <div>
                    <p style={{ margin: '5px 0', fontSize: '14px' }}>
                      <strong>Assigned to:</strong> {action.assignee_name?.[0] || 'Unassigned'}
                    </p>
                    <p style={{ margin: '5px 0', fontSize: '14px' }}>
                      <strong>Role:</strong> {action.assignee_role?.[0] || 'N/A'}
                    </p>
                    <p style={{ margin: '5px 0', fontSize: '14px' }}>
                      <strong>Department:</strong> {action.assignee_departments?.[0] || 'N/A'}
                    </p>
                  </div>

                  <div>
                    <p style={{ margin: '5px 0', fontSize: '14px' }}>
                      <strong>Deadline:</strong> 
                      <span style={{
                        color: action.deadline === '1_day' ? '#dc3545' : 
                              action.deadline === '3_days' ? '#fd7e14' : '#28a745',
                        fontWeight: 'bold',
                        marginLeft: '5px'
                      }}>
                        {action.deadline?.replace('_', ' ') || 'Not set'}
                      </span>
                    </p>
                    <p style={{ margin: '5px 0', fontSize: '14px' }}>
                      <strong>Deliverable:</strong> {action.deliverable || 'Not specified'}
                    </p>
                  </div>
                </div>

                {action.dependencies && action.dependencies.length > 0 && (
                  <div style={{ marginTop: '10px' }}>
                    <p style={{ margin: '5px 0', fontSize: '14px' }}>
                      <strong>Dependencies:</strong>
                    </p>
                    <ul style={{ margin: '5px 0', paddingLeft: '20px', fontSize: '13px' }}>
                      {action.dependencies.map((dependency, i) => (
                        <li key={i} style={{ color: '#6c757d' }}>
                          {dependency}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Progress/Status indicator */}
                <div style={{
                  marginTop: '15px',
                  padding: '8px 12px',
                  backgroundColor: '#e9ecef',
                  borderRadius: '4px',
                  fontSize: '12px',
                  color: '#495057',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <span>
                    <strong>Status:</strong> Pending
                  </span>
                  <span style={{
                    backgroundColor: action.priority === 'high' ? '#fff3cd' : 
                                  action.priority === 'medium' ? '#d1ecf1' : '#d4edda',
                    color: action.priority === 'high' ? '#856404' : 
                          action.priority === 'medium' ? '#0c5460' : '#155724',
                    padding: '2px 6px',
                    borderRadius: '3px',
                    fontSize: '11px'
                  }}>
                    {action.priority === 'high' ? '🔥 Urgent' : 
                    action.priority === 'medium' ? '⏰ Soon' : '✅ Scheduled'}
                  </span>
                </div>
              </div>
            ))}
            
            {/* Summary footer */}
            <div style={{
              marginTop: '20px',
              padding: '15px',
              backgroundColor: '#e7f3ff',
              borderRadius: '6px',
              fontSize: '14px',
              color: '#004085'
            }}>
              <strong>Summary:</strong> {actions.filter(a => a.priority === 'high').length} high priority, {' '}
              {actions.filter(a => a.priority === 'medium').length} medium priority, {' '}
              {actions.filter(a => a.priority === 'low').length} low priority items
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;