import React from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../auth";
import IndexTicker from "./IndexTicker";

/* 🌈 Colorful Icons */
const IconChat = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="chatGradient" x1="0" y1="0" x2="24" y2="24">
        <stop offset="0%" stopColor="#00B4DB" />
        <stop offset="100%" stopColor="#0083B0" />
      </linearGradient>
    </defs>
    <path
      d="M4 6.5A3.5 3.5 0 0 1 7.5 3h9A3.5 3.5 0 0 1 20 6.5v5A3.5 3.5 0 0 1 16.5 15H12l-3.8 3.2c-.6.5-1.2.1-1.2-.6V15A3.5 3.5 0 0 1 4 11.5v-5Z"
      stroke="url(#chatGradient)"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const IconPortfolio = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="portfolioGradient" x1="0" y1="0" x2="24" y2="24">
        <stop offset="0%" stopColor="#F7971E" />
        <stop offset="100%" stopColor="#FFD200" />
      </linearGradient>
    </defs>
    <path
      d="M4 18V6m5 12V10m5 8V8m5 10V4"
      stroke="url(#portfolioGradient)"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
  </svg>
);

const IconReport = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="reportGradient" x1="0" y1="0" x2="24" y2="24">
        <stop offset="0%" stopColor="#8E2DE2" />
        <stop offset="100%" stopColor="#4A00E0" />
      </linearGradient>
    </defs>
    <path
      d="M7 3h7l5 5v11a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z"
      stroke="url(#reportGradient)"
      strokeWidth="1.8"
    />
    <path
      d="M14 3v4a1 1 0 0 0 1 1h4"
      stroke="url(#reportGradient)"
      strokeWidth="1.8"
    />
    <path
      d="M8.5 14H15M8.5 17H13"
      stroke="url(#reportGradient)"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
  </svg>
);

export default function Sidebar({ collapsed, onToggle }) {
  const { user } = useAuth();
  const displayName = user?.name || user?.email?.split("@")[0] || "User";
  const initial = (displayName?.[0] || "U").toUpperCase();

  return (
    <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
      {/* top row: logo chip + collapse toggle */}
      <div className="brand-row small">
        <button className="toggle tiny" onClick={onToggle} aria-label="Toggle sidebar">
          {collapsed ? "›" : "‹"}
        </button>
      </div>

      {/* nav */}
      <nav className="nav compact">
        <NavLink to="/chat" className="nav-item" title="Talk with Market">
          <IconChat />
          <span>Talk with Market</span>
        </NavLink>

        <NavLink to="/portfolio" className="nav-item" title="Portfolio Chat">
          <IconPortfolio />
          <span>Talk with Portfolio</span>
        </NavLink>

        <NavLink to="/reports" className="nav-item" title="Portfolio Report">
          <IconReport />
          <span>Portfolio Report</span>
        </NavLink>
      </nav>

      <IndexTicker />

      {/* user inline chip at bottom */}
      <div className="sidebar-user small">
        <div className="sidebar-avatar tiny" aria-label={displayName}>
          {initial}
        </div>
        <div className="sidebar-identity">
          <div className="sidebar-name">{displayName}</div>
        </div>
      </div>
    </aside>
  );
}
