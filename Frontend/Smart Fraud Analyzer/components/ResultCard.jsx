import { useState } from "react";

function ResultCard({ result }) {
  if (!result) return null;

  const qrData = Array.isArray(result.qr_data)
    ? result.qr_data
    : result.qr_data
    ? [result.qr_data]
    : [];
  const urls = Array.isArray(result.urls) ? result.urls : [];
  const phones = Array.isArray(result.phone_numbers) ? result.phone_numbers : [];
  const emails = Array.isArray(result.emails) ? result.emails : [];
  const upiIds = Array.isArray(result.upi_ids) ? result.upi_ids : [];
  const timeline = Array.isArray(result.timeline)
  ? result.timeline
  : [];

const [showTimeline, setShowTimeline] = useState(false);
  const qrDetected = Boolean(result.qr_detected);
  const hasScreenshot =
    result.image_uploaded ||
    result.image_relevance !== "Not Applicable" ||
    result.relevance_score !== 0 ||
    !!result.ocr_text?.trim() ||
    qrDetected ||
    qrData.length > 0 ||
    urls.length > 0 ||
    phones.length > 0 ||
    emails.length > 0 ||
    upiIds.length > 0;

  const relevanceColor = (() => {
    const label = String(result.image_relevance ?? "").toLowerCase();
    if (label.includes("high")) return "#28a745"; // green
    if (label.includes("part")) return "#1d53b9"; // yellow
    if (label.includes("not")) return "#dc3545"; //red
    if (label.includes("relev")) return "#fd7e14"; // orange
    
    return "#000000";
  })();

  return (
    <div className="result-card">

      <h2>Prediction Result</h2>

      <hr />

      <p>
        <strong>Selected Fraud Category:</strong>
        <br />
        {result.selected_category}
      </p>

      <p>
        <strong>Predicted Fraud Category:</strong>
        <br />
        {result.predicted_category}
      </p>

      <p>
        <strong>Suggested IT Act Section:</strong>
        <br />
        {result.suggested_section}
      </p>

      {hasScreenshot ? (
        <>
          <div className="ocr-box">
            <h3>Extracted Text From Proof</h3>
            <p>{result.ocr_text?.trim() ? result.ocr_text : "No text detected."}</p>
          </div>

          <div className="relevance-box">
            <h3>Proof Relevance</h3>
            <p>
              <strong>Upload status:</strong> {result.image_uploaded ? "Received" : "Not received"}
            </p>
            <p>
              <strong>Status:</strong>{' '}
              {result.image_relevance}
            </p>
            <p>
              <strong>Similarity Score:</strong> {result.relevance_score}%
            </p>
          </div>

          <div className="indicator-box">
            <h3>Fraud Indicators Searched</h3>
  
            <p>
              <strong>QR Code:</strong> {qrDetected ? "Yes" : "No"}
            </p>

            {qrData.length > 0 && (
              <>
                <strong>QR Data:</strong>
                <ul>
                  {qrData.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </>
            )}

            {urls.length > 0 && (
              <>
                <strong>URLs:</strong>
                <ul>
                  {urls.map((url, index) => (
                    <li key={index}>{url}</li>
                  ))}
                </ul>
              </>
            )}

            {phones.length > 0 && (
              <>
                <strong>Phone Numbers:</strong>
                <ul>
                  {phones.map((phone, index) => (
                    <li key={index}>{phone}</li>
                  ))}
                </ul>
              </>
            )}

            {emails.length > 0 && (
              <>
                <strong>Email IDs:</strong>
                <ul>
                  {emails.map((email, index) => (
                    <li key={index}>{email}</li>
                  ))}
                </ul>
              </>
            )}

            {upiIds.length > 0 && (
              <>
                <strong>UPI IDs:</strong>
                <ul>
                  {upiIds.map((upi, index) => (
                    <li key={index}>{upi}</li>
                  ))}
                </ul>
              </>
            )}

            {!qrDetected && !qrData.length && !urls.length && !phones.length && !emails.length && !upiIds.length && (
              <p>No fraud indicators detected in the Proof.</p>
            )}
          </div>
        </>
      ) : (
        <div className="ocr-box">
          <h3>Proof</h3>
          <p>No proof uploaded or detected.</p>
        </div>
      )}

      {timeline.length > 0 && (
  <div className="timeline-section">

    <button
      type="button"
      className="timeline-toggle-btn"
      onClick={() => setShowTimeline(!showTimeline)}
    >
      {showTimeline ? "❌ Hide Timeline" : "📅 Show Timeline"}
    </button>

    {showTimeline && (
      <div className="timeline-box">

        <h3><u>Complaint & Proof Timeline</u> ⏳</h3>

        <div className="timeline">

          {timeline.map((item, index) => (
            <div
              className="timeline-item"
              key={index}
            >

              <div className="timeline-dot"></div>

              <div className="timeline-date">
                {new Date(
                  item.date + "T00:00:00"
                ).toLocaleDateString(
                  "en-IN",
                  {
                    day: "2-digit",
                    month: "short",
                    year: "numeric"
                  }
                )}
              </div>

              <div className="timeline-time">
                🕒 {item.time || "Time not available"}
              </div>

              <div className="timeline-content">

                <strong>{item.source}</strong>

                <p>{item.event}</p>

              </div>
            </div>
          ))}

        </div>
      </div>
    )}

  </div>
  )} 

      <hr />

          {result.match ? (
        <div
          style={{
            background: "#d4edda",
            color: "#155724",
            padding: "15px",
            borderRadius: "8px",
            marginTop: "15px",
          }}
        >
          ✅ The complaint matches the selected fraud category. The Proof Submitted is <span  style={{ color: relevanceColor, fontWeight: 600 }}>{result.image_relevance}</span>.
        </div>
      ) : (
        <div
          style={{
            background: "#f8d7da",
            color: "#721c24",
            padding: "15px",
            borderRadius: "8px",
            marginTop: "15px",
          }}
        >
          <h3>Category Mismatch</h3>

          <p>
            The complaint does not belong to the selected category.
          </p>

          <p>
            <strong>Suggested Fraud Category:</strong>
            <br />
            {result.predicted_category}
          </p>

          <p>
            <strong>Suggested IT Act Section:</strong>
            <br />
            {result.suggested_section}
          </p>
          <br/>
          <p>
            <strong>Note:</strong> The Proof Submitted is <span  style={{ color: relevanceColor, fontWeight: 600 }}>{result.image_relevance}</span>. Please ensure that the uploaded Proof is relevant to the complaint. If it is not, consider uploading a more appropriate Proof for better analysis.
          </p>
        </div>
      
      )}
    </div>
  );
}

export default ResultCard;