import { useState } from "react";
import ResultCard from "./ResultCard";

function getLocalDateTime() {
  const now = new Date();
  const pad = (value) => String(value).padStart(2, "0");

  return [
    `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`,
    `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`,
  ].join("T");
}

function ComplaintForm() {
  const [complaint, setComplaint] = useState("");
  const [category, setCategory] = useState("");
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

   const handleImageChange = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    setImage(file);
    setPreview(URL.createObjectURL(file));
  };
  const handleSubmit = async () => {
    if (complaint.trim() === "") {
      alert("Please enter a complaint.");
      return;
    }

    if (category === "") {
      alert("Please select a fraud category.");
      return;
    }
     if (image === null) {
      alert("Please upload a proof image.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("complaint", complaint);
      formData.append("selected_category", category);
      formData.append("analysis_time", getLocalDateTime());
      if (image) {
        const safeImage = new File(
          [image.slice(0, image.size, image.type)],
          image.name,
          { type: image.type, lastModified: image.lastModified }
        );
        formData.append("image", safeImage);
      }

      console.log("Submitting image:", image);
      for (const pair of formData.entries()) {
        console.log(pair[0], pair[1]);
      }

      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        body: formData,
        headers: {
          Accept: "application/json",
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Server returned error:", response.status, errorText);
        alert("Unable to upload image to Flask server. Please try again.");
        setLoading(false);
        return;
      }

      const data = await response.json();
      console.log("Predict response:", data);
      setResult(data);
    } catch (error) {
      console.error("Predict request error:", error);
      alert("Unable to upload image to Flask server. Please try again.");
    }

    setLoading(false);
  };

  return (
    <div className="form-container">
      <h2>Smart Fraud Complaint Analyzer</h2>

      <textarea
        rows="8"
        placeholder="Enter your complaint here..."
        value={complaint}
        onChange={(e) => setComplaint(e.target.value)}
      />

      <select
        value={category}
        onChange={(e) => setCategory(e.target.value)}
      >
        <option value="">Select Fraud Category</option>
        <option value="Unauthorized Access / Hacking">Unauthorized Access / Hacking</option>
        <option value="Data Breach / Failure to Protect Data">Data Breach / Failure to Protect Data</option>
        <option value="Computer Related Offences">Computer Related Offences</option>
        <option value="Identity Theft">Identity Theft</option>
        <option value="OTP Fraud">OTP Fraud</option>
        <option value="Phishing Scam">Phishing Scam</option>
        <option value="Fake Bank Call">Fake Bank Call</option>
        <option value="Fake Customer Care Scam">Fake Customer Care Scam</option>
        <option value="UPI Fraud">UPI Fraud</option>
        <option value="QR Code Scam">QR Code Scam</option>
        <option value="KYC Update Scam">KYC Update Scam</option>
        <option value="Privacy Violation">Privacy Violation</option>
      </select>

         <label className="upload-label">

        Upload Proof (Image or PDF)

      </label>

      <input
        type="file"
        name="image"
        accept="image/*,.pdf,application/pdf"
        onChange={handleImageChange}
      />

      {preview && (
        <div className="preview">

          <img
            src={preview}
            alt="preview"
          />

        </div>
      )}

      <button type="button" onClick={handleSubmit}>
        {loading ? "Analyzing..." : "Analyze Complaint"}
      </button>

      <ResultCard result={result} />
    </div>
  );
}

export default ComplaintForm;