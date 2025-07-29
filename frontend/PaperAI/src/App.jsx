import React from "react";

// --- Subscription Page Component ---
// A new component to display subscription options.
const SubscriptionPage = ({ onBack }) => {
  // --- Style Objects for Subscription Page ---
  const pageStyle = {
    width: "100%",
    maxWidth: "1200px",
    margin: "0 auto",
    padding: "6rem 2rem 2rem",
    textAlign: "center",
    color: "#334155",
  };

  const headerStyle = {
    fontSize: "2.5rem",
    fontWeight: "bold",
    color: "#1e293b",
    marginBottom: "1rem",
  };

  const subheaderStyle = {
    fontSize: "1.2rem",
    color: "#64748b",
    maxWidth: "600px",
    margin: "0 auto 2.5rem auto",
  };

  const pricingGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
    gap: "2rem",
    marginTop: "3rem",
  };

  const cardStyle = (isFeatured) => ({
    backgroundColor: "white",
    borderRadius: "1rem",
    padding: "2rem",
    boxShadow: isFeatured
      ? "0 20px 25px -5px rgba(99, 102, 241, 0.2), 0 10px 10px -5px rgba(99, 102, 241, 0.1)"
      : "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    border: isFeatured ? "2px solid #6366f1" : "1px solid #e2e8f0",
    textAlign: "left",
    position: "relative",
    transform: isFeatured ? "scale(1.05)" : "scale(1)",
    transition: "transform 0.3s ease, box-shadow 0.3s ease",
  });

  const planNameStyle = {
    fontSize: "1.25rem",
    fontWeight: "bold",
    color: "#1e293b",
  };

  const priceStyle = {
    fontSize: "3rem",
    fontWeight: "bold",
    color: "#1e293b",
    margin: "1rem 0",
  };

  const featureListStyle = {
    listStyle: "none",
    padding: 0,
    margin: "2rem 0",
  };

  const featureItemStyle = {
    display: "flex",
    alignItems: "center",
    marginBottom: "1rem",
    color: "#475569",
  };

  const checkmarkIcon = (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{ color: "#4ade80", marginRight: "0.75rem" }}
    >
      <polyline points="20 6 9 17 4 12"></polyline>
    </svg>
  );

  const buttonStyle = (isFeatured) => ({
    width: "100%",
    padding: "0.75rem",
    borderRadius: "9999px",
    border: "none",
    cursor: "pointer",
    fontWeight: "bold",
    fontSize: "1rem",
    backgroundColor: isFeatured ? "#6366f1" : "#f1f5f9",
    color: isFeatured ? "white" : "#1e293b",
    transition: "background-color 0.3s ease",
  });

  const backButtonStyle = {
    marginTop: "3rem",
    backgroundColor: "#6b7280",
    color: "white",
    fontWeight: "bold",
    padding: "0.75rem 2rem",
    borderRadius: "9999px",
    border: "none",
    cursor: "pointer",
    fontSize: "1rem",
    transition: "background-color 0.3s ease",
  };

  return (
    <div style={pageStyle}>
      <h1 style={headerStyle}>Choose Your Plan</h1>
      <p style={subheaderStyle}>
        Simple, transparent pricing. No hidden fees. Choose the plan that's
        right for you.
      </p>

      <div style={pricingGridStyle}>
        {/* Basic Plan */}
        <div style={cardStyle(false)}>
          <h2 style={planNameStyle}>Basic</h2>
          <p style={priceStyle}>
            $10
            <span style={{ fontSize: "1rem", color: "#64748b" }}>/month</span>
          </p>
          <ul style={featureListStyle}>
            <li style={featureItemStyle}>{checkmarkIcon} 5 Analyses per Day</li>
            <li style={featureItemStyle}>{checkmarkIcon} Standard Support</li>
            <li style={featureItemStyle}>{checkmarkIcon} Basic Analytics</li>
          </ul>
          <button style={buttonStyle(false)}>Choose Basic</button>
        </div>

        {/* Pro Plan (Featured) */}
        <div style={cardStyle(true)}>
          <h2 style={planNameStyle}>Pro</h2>
          <p style={priceStyle}>
            $25
            <span style={{ fontSize: "1rem", color: "#64748b" }}>/month</span>
          </p>
          <ul style={featureListStyle}>
            <li style={featureItemStyle}>{checkmarkIcon} Unlimited Analyses</li>
            <li style={featureItemStyle}>{checkmarkIcon} Priority Support</li>
            <li style={featureItemStyle}>{checkmarkIcon} Advanced Analytics</li>
            <li style={featureItemStyle}>{checkmarkIcon} Team Collaboration</li>
          </ul>
          <button style={buttonStyle(true)}>Choose Pro</button>
        </div>

        {/* Enterprise Plan */}
        <div style={cardStyle(false)}>
          <h2 style={planNameStyle}>Enterprise</h2>
          <p style={priceStyle}>Contact Us</p>
          <ul style={featureListStyle}>
            <li style={featureItemStyle}>{checkmarkIcon} All Pro Features</li>
            <li style={featureItemStyle}>
              {checkmarkIcon} Dedicated Account Manager
            </li>
            <li style={featureItemStyle}>
              {checkmarkIcon} Custom Integrations
            </li>
          </ul>
          <button style={buttonStyle(false)}>Contact Sales</button>
        </div>
      </div>

      <button style={backButtonStyle} onClick={onBack}>
        Back to Uploader
      </button>
    </div>
  );
};

// Main App component
export default function App() {
  // State to control which page is visible
  const [currentPage, setCurrentPage] = React.useState("upload"); // 'upload' or 'subscription'

  // State for the selected file objects
  const [answerKeyFile, setAnswerKeyFile] = React.useState(null);
  const [responsesFile, setResponsesFile] = React.useState(null);

  // State for displaying the selected file names
  const [answerKeyName, setAnswerKeyName] = React.useState("");
  const [responsesName, setResponsesName] = React.useState("");

  // State for API communication
  const [isLoading, setIsLoading] = React.useState(false);
  const [statusMessage, setStatusMessage] = React.useState("");
  const [isError, setIsError] = React.useState(false);

  // State to hold the output file details for downloading
  const [outputFiles, setOutputFiles] = React.useState(null); // This will now store the batch and the Excel filename

  // State to manage hover effects
  const [isLabel1Hovered, setLabel1Hovered] = React.useState(false);
  const [isLabel2Hovered, setLabel2Hovered] = React.useState(false);
  const [isButtonHovered, setButtonHovered] = React.useState(false);

  // Handler for the first file input (Answer Key)
  const handleFileChange1 = (event) => {
    const file = event.target.files[0];
    if (file) {
      setAnswerKeyFile(file);
      setAnswerKeyName(`Selected: ${file.name}`);
    } else {
      setAnswerKeyFile(null);
      setAnswerKeyName("");
    }
  };

  // Handler for the second file input (Student Responses)
  const handleFileChange2 = (event) => {
    const file = event.target.files[0];
    if (file) {
      setResponsesFile(file);
      setResponsesName(`Selected: ${file.name}`);
    } else {
      setResponsesFile(null);
      setResponsesName("");
    }
  };

  // Handler for submitting files to the backend
  const handleSubmit = async () => {
    if (!answerKeyFile || !responsesFile) {
      setStatusMessage(
        "Please select both the answer key and the responses file."
      );
      setIsError(true);
      return;
    }

    setIsLoading(true);
    setStatusMessage("Uploading and analyzing files...");
    setIsError(false);
    setOutputFiles(null); // Clear previous output files

    const formData = new FormData();
    formData.append("answer_key", answerKeyFile);
    formData.append("student_responses", responsesFile);

    try {
      // Simulate a network delay for the loading animation
      await new Promise((resolve) => setTimeout(resolve, 2500)); // Increased duration

      const response = await fetch(
        "http://127.0.0.1:8000/upload-and-analyze/",
        {
          method: "POST",
          body: formData,
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "An unknown error occurred.");
      }

      setStatusMessage("Analysis complete! Your files are ready for download.");
      setIsError(false);

      const batchName = result.batch_directory.split(/[\/\\]/).pop();
      // Store the batch name and the Excel file name
      setOutputFiles({
        batch: batchName,
        excelReport: "item_analysis_report.xlsx", // This is the fixed name from your backend
      });

      setAnswerKeyFile(null);
      setResponsesFile(null);
      setAnswerKeyName("");
      setResponsesName("");
    } catch (error) {
      setStatusMessage(`Error: ${error.message}`);
      setIsError(true);
    } finally {
      setIsLoading(false);
    }
  };

  // Resets the UI to its initial state for a new analysis
  const handleReset = () => {
    setOutputFiles(null);
    setStatusMessage("");
    setIsError(false);
    setCurrentPage("upload");
  };

  // --- Style Objects ---
  const appContainerStyle = {
    width: "100%",
    minHeight: "100vh",
    position: "relative",
    overflow: "hidden",
  };
  const headerStyle = {
    position: "fixed",
    top: "1rem",
    left: "50%",
    transform: "translateX(-50%)",
    zIndex: 20,
    width: "90%",
  };
  const capsuleNavStyle = {
    width: "100%",
    maxWidth: "800px",
    backgroundColor: "rgba(255, 255, 255, 0.8)",
    backdropFilter: "blur(12px) saturate(180%)",
    WebkitBackdropFilter: "blur(12px) saturate(180%)",
    border: "1px solid rgba(224, 231, 255, 0.7)",
    borderRadius: "9999px",
    boxShadow:
      "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)",
    padding: "0.5rem 1.5rem",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    margin: "0 auto",
  };
  const verticalTextContainerStyle = {
    position: "absolute",
    top: "50%",
    right: "0",
    transform: "translateY(-50%) translateX(40%)",
    zIndex: 0,
  };
  const verticalTextStyle = {
    fontSize: "24vw",
    fontWeight: "900",
    color: "transparent", // Makes the text fill transparent
    WebkitTextStroke: "2px #c7d2fe", // Creates a 2px outline
    writingMode: "vertical-rl",
    transform: "rotate(180deg)",
    whiteSpace: "nowrap",
    userSelect: "none",
    letterSpacing: "-2.5rem",
  };
  const mainStyle = {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
    zIndex: 10,
    padding: "0 1rem",
  };
  const contentWrapperStyle = {
    width: "100%",
    maxWidth: "56rem",
    textAlign: "center",
  };
  const fileInputsContainerStyle = {
    display: "flex",
    flexDirection: "column",
    gap: "1.5rem",
    justifyContent: "center",
    alignItems: "center",
  };
  const fileInputRowStyle = {
    display: "flex",
    gap: "1.5rem",
    width: "100%",
    justifyContent: "center",
    alignItems: "flex-start",
  };
  const fileInputWrapperStyle = { flex: 1, maxWidth: "28rem" };
  const fileInputLabelStyle = (isHovered) => ({
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    width: "100%",
    height: "14rem",
    border: `2px dashed ${isHovered ? "#6366f1" : "#e0e7ff"}`,
    borderRadius: "1rem",
    cursor: "pointer",
    backgroundColor: isHovered ? "#fefdff" : "#ffffff",
    transition: "all 0.3s ease",
  });
  const p1Style = {
    marginBottom: "0.5rem",
    fontSize: "0.875rem",
    color: "rgb(107, 114, 128)",
  };
  const p1SpanStyle = { fontWeight: "600", color: "#6366f1" };
  const p2Style = { fontSize: "0.75rem", color: "rgb(156, 163, 175)" };
  const fileNameStyle = {
    marginTop: "1rem",
    fontSize: "0.875rem",
    color: "rgb(75, 85, 99)",
    height: "1.25rem",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  };
  const analyzeButtonStyle = {
    backgroundColor:
      !answerKeyFile || !responsesFile || isLoading ? "#a5b4fc" : "#4f46e5",
    color: "white",
    fontWeight: "bold",
    padding: "0.75rem 2rem",
    borderRadius: "9999px",
    border: "none",
    cursor:
      !answerKeyFile || !responsesFile || isLoading ? "not-allowed" : "pointer",
    boxShadow:
      "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    fontSize: "1rem",
    marginTop: "1.5rem",
    transition:
      "background-color 0.3s ease-in-out, box-shadow 0.3s ease-in-out",
    transform: isLoading ? "scale(0.95)" : "scale(1)",
  };
  const statusMessageStyle = {
    marginTop: "1.5rem",
    minHeight: "1.5rem",
    fontSize: "0.875rem",
    fontWeight: "500",
    color: isError ? "#ef4444" : "#16a34a",
    transition: "color 0.3s ease-in-out",
  };
  const resultsContainerStyle = {
    marginTop: "2rem",
    backgroundColor: "white",
    padding: "2rem",
    borderRadius: "1rem",
    boxShadow:
      "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
  };
  const downloadButtonsContainerStyle = {
    display: "flex",
    justifyContent: "center",
    gap: "1rem",
    marginTop: "1rem",
  };
  const downloadButtonStyle = {
    textDecoration: "none",
    backgroundColor: "#4f46e5",
    color: "white",
    fontWeight: "bold",
    padding: "0.6rem 1.5rem",
    borderRadius: "9999px",
    border: "none",
    cursor: "pointer",
    boxShadow:
      "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
    fontSize: "0.875rem",
    transition: "background-color 0.3s ease-in-out",
  };
  const resetButtonStyle = {
    ...analyzeButtonStyle,
    marginTop: "1.5rem",
    backgroundColor: "#6b7280",
  };
  const navButtonStyle = {
    backgroundColor: isButtonHovered ? "#4f46e5" : "#6366f1",
    color: "white",
    fontWeight: "700",
    padding: "0.5rem 1.25rem",
    borderRadius: "9999px",
    border: "none",
    cursor: "pointer",
    boxShadow:
      "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
    transition: "background-color 0.3s ease-in-out",
  };

  // New styles for the description
  const descriptionHeaderStyle = {
    fontSize: "2rem",
    fontWeight: "bold",
    color: "#312e81",
    marginBottom: "0.5rem",
  };

  const descriptionTextStyle = {
    fontSize: "1.3rem",
    fontWeight: "400",
    maxWidth: "600px",
    margin: "0 auto 2.5rem auto",
    lineHeight: "1.7",
    // Creates a subtle gradient text effect
    background: "linear-gradient(90deg, #4338ca, #6366f1)",
    WebkitBackgroundClip: "text",
    backgroundClip: "text",
    color: "transparent",
    letterSpacing: "0.5px",
    marginTop: "1.3vw",
  };

  // New styles for the loading animation
  const loaderContainerStyle = {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "300px",
  };

  const spinnerStyle = {
    display: "flex",
    gap: "0.5rem",
  };

  const dotStyle = (delay) => ({
    width: "12px",
    height: "12px",
    backgroundColor: "#6366f1",
    borderRadius: "50%",
    animation: `pulse 1.4s infinite ease-in-out both`,
    animationDelay: delay,
  });

  const loadingTextStyle = {
    marginTop: "2rem",
    fontSize: "1rem",
    fontWeight: "500",
    color: "#4f46e5",
  };

  return (
    <>
      <style>{` 
        html, body, #root { margin: 0; padding: 0; width: 100%; height: 100%; font-family: "Inter", sans-serif; background-color: #f8f7ff; } 
        @keyframes pulse {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1.0); }
        }
      `}</style>
      <div style={appContainerStyle}>
        <header style={headerStyle}>
          <nav style={capsuleNavStyle}>
            <svg
              width="48"
              height="48"
              viewBox="0 0 100 100"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                <linearGradient
                  id="grad_arrow"
                  x1="0%"
                  y1="0%"
                  x2="100%"
                  y2="100%"
                >
                  <stop
                    offset="0%"
                    style={{ stopColor: "#4338ca", stopOpacity: 1 }}
                  />
                  <stop
                    offset="100%"
                    style={{ stopColor: "#6366f1", stopOpacity: 1 }}
                  />
                </linearGradient>
              </defs>
              <path
                d="M50 8C26.8 8 8 26.8 8 50C8 73.2 26.8 92 50 92C73.2 92 92 73.2 92 50C92 26.8 73.2 8 50 8Z"
                fill="url(#grad_arrow)"
              />
              <path
                d="M42 68L62 50L42 32"
                stroke="white"
                strokeWidth="8"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <button
              style={navButtonStyle}
              onMouseEnter={() => setButtonHovered(true)}
              onMouseLeave={() => setButtonHovered(false)}
              onClick={() => setCurrentPage("subscription")}
            >
              Avail Subscription
            </button>
          </nav>
        </header>

        <main style={mainStyle}>
          {currentPage === "subscription" && (
            <SubscriptionPage onBack={() => setCurrentPage("upload")} />
          )}

          {currentPage === "upload" && (
            <>
              <div style={verticalTextContainerStyle}>
                <h1 style={verticalTextStyle}>ExA</h1>
              </div>
              <div style={contentWrapperStyle}>
                {isLoading ? (
                  <div style={loaderContainerStyle}>
                    <div style={spinnerStyle}>
                      <div style={dotStyle("0s")}></div>
                      <div style={dotStyle("0.2s")}></div>
                      <div style={dotStyle("0.4s")}></div>
                    </div>
                    <p style={loadingTextStyle}>Analyzing your files...</p>
                  </div>
                ) : !outputFiles ? ( // If outputFiles is null, show upload UI
                  <div style={fileInputsContainerStyle}>
                    <h1 style={descriptionHeaderStyle}>Post Exam Analyser</h1>
                    <p style={descriptionTextStyle}>
                      Upload your answer key and student responses to instantly
                      generate a detailed item analysis, including difficulty,
                      discrimination, and distractor efficiency.
                    </p>
                    <div style={fileInputRowStyle}>
                      <div style={fileInputWrapperStyle}>
                        <label
                          htmlFor="file-upload-input-1"
                          style={fileInputLabelStyle(isLabel1Hovered)}
                          onMouseEnter={() => setLabel1Hovered(true)}
                          onMouseLeave={() => setLabel1Hovered(false)}
                        >
                          <div
                            style={{
                              display: "flex",
                              flexDirection: "column",
                              alignItems: "center",
                              justifyContent: "center",
                              paddingTop: "1.25rem",
                              paddingBottom: "1.5rem",
                            }}
                          >
                            <svg
                              style={{
                                width: "2.5rem",
                                height: "2.5rem",
                                marginBottom: "1rem",
                                color: "#a5b4fc",
                              }}
                              aria-hidden="true"
                              xmlns="http://www.w3.org/2000/svg"
                              fill="none"
                              viewBox="0 0 20 16"
                            >
                              <path
                                stroke="currentColor"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
                              />
                            </svg>
                            <p style={p1Style}>
                              <span style={p1SpanStyle}>Upload Answer Key</span>
                            </p>
                            <p style={p2Style}>CSV file</p>
                          </div>
                          <input
                            id="file-upload-input-1"
                            type="file"
                            style={{ display: "none" }}
                            onChange={handleFileChange1}
                            accept=".csv"
                          />
                        </label>
                        <p style={fileNameStyle} title={answerKeyName}>
                          {answerKeyName}
                        </p>
                      </div>
                      <div style={fileInputWrapperStyle}>
                        <label
                          htmlFor="file-upload-input-2"
                          style={fileInputLabelStyle(isLabel2Hovered)}
                          onMouseEnter={() => setLabel2Hovered(true)}
                          onMouseLeave={() => setLabel2Hovered(false)}
                        >
                          <div
                            style={{
                              display: "flex",
                              flexDirection: "column",
                              alignItems: "center",
                              justifyContent: "center",
                              paddingTop: "1.25rem",
                              paddingBottom: "1.5rem",
                            }}
                          >
                            <svg
                              style={{
                                width: "2.5rem",
                                height: "2.5rem",
                                marginBottom: "1rem",
                                color: "#a5b4fc",
                              }}
                              aria-hidden="true"
                              xmlns="http://www.w3.org/2000/svg"
                              fill="none"
                              viewBox="0 0 20 16"
                            >
                              <path
                                stroke="currentColor"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
                              />
                            </svg>
                            <p style={p1Style}>
                              <span style={p1SpanStyle}>Upload Responses</span>
                            </p>
                            <p style={p2Style}>CSV file</p>
                          </div>
                          <input
                            id="file-upload-input-2"
                            type="file"
                            style={{ display: "none" }}
                            onChange={handleFileChange2}
                            accept=".csv"
                          />
                        </label>
                        <p style={fileNameStyle} title={responsesName}>
                          {responsesName}
                        </p>
                      </div>
                    </div>
                    <button
                      style={analyzeButtonStyle}
                      onClick={handleSubmit}
                      disabled={!answerKeyFile || !responsesFile || isLoading}
                    >
                      {isLoading ? "Analyzing..." : "Run Analysis"}
                    </button>
                  </div>
                ) : (
                  // If outputFiles is available, show download button
                  <div style={resultsContainerStyle}>
                    <h2 style={{ color: "#312e81", marginTop: 0 }}>Results</h2>
                    <div style={downloadButtonsContainerStyle}>
                      <a
                        href={`https://exanalyzer-backend.vercel.app/download/${outputFiles.batch}/${outputFiles.excelReport}`}
                        style={downloadButtonStyle}
                        download // This attribute prompts the browser to download the file
                      >
                        Download Complete Analysis
                      </a>
                    </div>
                    <button style={resetButtonStyle} onClick={handleReset}>
                      Generate Again
                    </button>
                  </div>
                )}
                <div style={statusMessageStyle}>{statusMessage}</div>
              </div>
            </>
          )}
        </main>
      </div>
    </>
  );
}
