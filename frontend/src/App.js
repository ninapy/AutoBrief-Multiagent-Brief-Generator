import React, { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [pdfUrl, setPdfUrl] = useState(null);

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
      setStatus("✅ Brief generated!");
    } catch (err) {
      console.error(err);
      setStatus("❌ Error: " + err.message);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>Creative Brief Generator</h1>
      <form onSubmit={handleUpload}>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          required
        />
        <button type="submit">Generate Brief</button>
      </form>

      <div style={{ marginTop: "1rem" }}>{status}</div>

      {pdfUrl && (
        <div style={{ marginTop: "1rem" }}>
          <a href={pdfUrl} download="brief_output.pdf">Download Brief PDF</a>
        </div>
      )}
    </div>
  );
}

export default App;
