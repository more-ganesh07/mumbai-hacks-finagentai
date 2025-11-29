import React, { useState } from "react";
import Sidebar from "../components/Sidebar";
import { useAuth } from "../auth";
import { Navigate } from "react-router-dom";
import { generatePortfolioReport } from "../services/api";

export default function Reports() {
  const { user } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [reportStatus, setReportStatus] = useState(null);
  const [error, setError] = useState(null);

  if (!user) return <Navigate to="/login" replace />;

  const run = async () => {
    setLoading(true);
    setError(null);
    setReportStatus(null);

    try {
      const result = await generatePortfolioReport();
      setReportStatus(result);
    } catch (err) {
      console.error("Report generation error:", err);
      setError(err.message || "Failed to generate report");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`app-shell ${collapsed ? "collapsed" : ""}`}>
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(x => !x)} />
      <section className="main">
        <div className="header">
          <div>
            <div style={{ fontWeight: 700, fontSize: "1.2rem" }}>Portfolio Report</div>
            <div className="mini">
              Generate and email a comprehensive portfolio summary.
            </div>
          </div>
          <button
            className="button"
            onClick={run}
            disabled={loading}
            style={{
              opacity: loading ? 0.5 : 1,
              cursor: loading ? "not-allowed" : "pointer"
            }}
          >
            {loading ? "Generating…" : "Generate Report"}
          </button>
        </div>

        <div className="content" style={{ gridTemplateRows: "auto 1fr", padding: "24px" }}>
          {error && (
            <div style={{
              background: "rgba(255,0,0,0.1)",
              border: "1px solid rgba(255,0,0,0.3)",
              borderRadius: "12px",
              padding: "16px",
              marginBottom: "16px",
              color: "#ff6b6b"
            }}>
              <div style={{ fontSize: 16, fontWeight: 700, marginBottom: "8px" }}>Error</div>
              <div>{error}</div>
            </div>
          )}

          {reportStatus && (
            <div style={{
              background: "rgba(0,255,0,0.05)",
              border: "1px solid rgba(0,255,0,0.2)",
              borderRadius: "16px",
              padding: "16px",
              marginBottom: "16px"
            }}>
              <div style={{ fontSize: 18, fontWeight: 700, marginBottom: "8px", color: "#4ade80" }}>
                ✓ Success
              </div>
              <div style={{ color: "rgba(255,255,255,0.85)" }}>
                {reportStatus.message || "Portfolio report generated and emailed successfully!"}
              </div>
            </div>
          )}

          {!reportStatus && !error && !loading && (
            <div style={{
              background: "var(--card)",
              border: "1px solid rgba(255,255,255,.06)",
              borderRadius: "16px",
              padding: "24px",
              textAlign: "center"
            }}>
              <div style={{ fontSize: 18, fontWeight: 700, marginBottom: "12px" }}>
                Ready to Generate Report
              </div>
              <div className="hint" style={{ marginBottom: "20px" }}>
                Click "Generate Report" to create a comprehensive portfolio summary.
                The report will be generated and sent to your registered email address.
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
