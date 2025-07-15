import React, { useState, useRef } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [pdfUrl, setPdfUrl] = useState(null);
  const inputRef = useRef();

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

    setStatus("Uploading...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/brief", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Brief generation failed");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      setPdfUrl(url);
      setStatus("Brief generated!");
    } catch (err) {
      console.error(err);
      setStatus("Error: " + err.message);
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
              setStatus("");
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
          </div>
        )}
      </div>

    </div>
  );
}

export default App;