import Navbar from "../components/Navbar";
import ComplaintForm from "../components/ComplaintForm";
import Footer from "../components/Footer";

function App() {
    const CATEGORIES = [
        { name: "OTP Fraud", section: "Section 66D", keywords: ["otp", "one time password", "one-time password"] },
        { name: "KYC Update Scam", section: "Section 66D", keywords: ["kyc", "know your customer"] },
        { name: "Fake Customer Care Scam", section: "Section 66D", keywords: ["customer care", "customer support", "remote access app", "anydesk", "teamviewer", "helpline"] },
        { name: "QR Code Scam", section: "Section 66D", keywords: ["qr code", "scanned the qr", "scan qr"] },
        { name: "Unauthorized Access / Hacking", section: "Section 43", keywords: ["hacked", "hacker", "unauthorized access", "ransomware", "malicious software", "malware", "server"] },
        { name: "Data Breach / Failure to Protect Data", section: "Section 43A", keywords: ["data breach", "database", "leaked", "exposed my", "security breach"] },
        { name: "Identity Theft", section: "Section 66C", keywords: ["aadhaar", "pan card", "digital signature", "impersonat", "username and password", "identity"] },
        { name: "Computer Related Offences", section: "Section 66", keywords: ["virus", "tampered", "deleted", "corrupted", "computer"] },
        { name: "Fake Bank Call", section: "Section 66D", keywords: ["bank executive", "bank official", "claiming to be from", "bank representative"] },
        { name: "Privacy Violation", section: "Section 66E", keywords: ["private photo", "privacy", "without consent", "morphed", "captured images"] },
        { name: "Phishing Scam", section: "Section 66D", keywords: ["phishing", "fake link", "fake website", "clicked a link"] },
        { name: "UPI Fraud", section: "Section 66D", keywords: ["upi", "google pay", "phonepe", "upi pin"] },
        { name: "Fake Job Scam", section: "Section 66D", keywords: ["job offer", "registration fee", "work from home", "recruiter"] },
        { name: "Fake Social Engineering Scam", section: "Section 66D", keywords: ["social media", "friend request", "emotional", "trust me"] },
        { name: "Fake Tech Support Scam", section: "Section 66D", keywords: ["tech support", "computer virus alert", "pop up warning", "remote access"] },
        { name: "Fake Rental Scam", section: "Section 66D", keywords: ["rental", "landlord", "advance rent", "property listing"] },
        { name: "Fake Government Official Scam", section: "Section 66D", keywords: ["government official", "income tax officer", "police officer", "customs officer"] },
    ];

    return (
        <>
            <Navbar />
            <div className="container" id="container">
                <ComplaintForm />
            </div>
        {/* HOW IT WORKS  */}
      <section className="section" id="how">
        <div className="section-eyebrow">Process</div>
        <h2 className="section-title">From complaint to citation, in three checks.</h2>
        <div className="steps">
          <div className="step">
            <div className="step-num">01 — WRITE</div>
            <h3>Describe the incident</h3>
            <p>Write what happened in plain language and choose the category you believe applies — no legal terminology required.</p>
          </div>
          <div className="step">
            <div className="step-num">02 — UPLOAD</div>
            <h3>Upload proof</h3>
            <p>Upload an image or PDF of all the required Relevant Documents invoving the Date and Time of the incident supporting your complaint.</p>
          </div>
          <div className="step">
            <div className="step-num">03 — VERIFY</div>
            <h3>Match is confirmed</h3>
            <p>If your selection agrees with the prediction, it's verified. If not, you get the suggested category ,its IT Act section and its Proof relevance.</p>
          </div>
        </div>
      </section>

      {/* CATEGORIES */}
      <section className="section cat-band" id="categories">
        <div className="section-eyebrow">Index</div>
        <h2 className="section-title">Fraud categories &amp; their IT Act sections.</h2>
        <div className="cat-grid">
          {CATEGORIES.map((c) => (
            <div className="cat-chip" key={c.name}>
              <div className="cat-chip-name">{c.name}</div>
              <div className="cat-chip-section">{c.section}</div>
            </div>
          ))}
        </div>
      </section>
            <Footer />
        </>
    );
}

export default App;