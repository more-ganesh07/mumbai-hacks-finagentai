import React, { useEffect, useRef, useState } from "react";
import Sidebar from "../components/Sidebar";
import ChatInput from "../components/ChatInput";
import ChatMessage from "../components/ChatMessage";
import { useAuth } from "../auth";
import { Navigate } from "react-router-dom";
import AITextLoading from "../components/AITextLoading";
import { marketChatbotSync } from "../services/api";

export default function Chat() {
  const { user } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [msgs, setMsgs] = useState([
    { role: "bot", text: "Hi! Ask me anything about market conditions.", timestamp: new Date() },
  ]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  const userHasSentMessage = msgs.some((m) => m.role === "user");

  useEffect(() => {
    if (scrollRef.current)
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [msgs, loading]);

  if (!user) return <Navigate to="/login" replace />;

  const handleSend = async (q) => {
    const userMsg = { role: "user", text: q, timestamp: new Date() };
    setMsgs((m) => [...m, userMsg]);
    setLoading(true);

    try {
      // Use the new marketChatbotSync API
      const data = await marketChatbotSync(q);

      // If the backend returns an empty/whitespace response, show fallback message
      const botReply =
        data && typeof data.response === "string" && data.response.trim()
          ? data.response
          : "Sorry — I couldn't get a reply from the server. Please try again.";

      setMsgs((m) => [...m, { role: "bot", text: botReply, timestamp: new Date() }]);
    } catch (e) {
      console.error("Market chatbot error:", e);

      // Friendly error text for the user
      const friendly = `Sorry, something went wrong while contacting the market assistant. ${e.message || ''}`;

      setMsgs((m) => [...m, { role: "bot", text: friendly, timestamp: new Date() }]);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = async (index, newText) => {
    // Keep messages up to the edited one, and update the edited message
    const newMsgs = msgs.slice(0, index + 1);
    newMsgs[index] = { ...newMsgs[index], text: newText, timestamp: new Date() };
    setMsgs(newMsgs);

    setLoading(true);
    try {
      // Use the new marketChatbotSync API
      const data = await marketChatbotSync(newText);

      const botReply =
        data && typeof data.response === "string" && data.response.trim()
          ? data.response
          : "Sorry — I couldn't get a reply from the server. Please try again.";

      setMsgs((m) => [...m, { role: "bot", text: botReply, timestamp: new Date() }]);
    } catch (e) {
      console.error("Market chatbot error:", e);
      const friendly = `Sorry, something went wrong while contacting the market assistant. ${e.message || ''}`;
      setMsgs((m) => [...m, { role: "bot", text: friendly, timestamp: new Date() }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`app-shell ${collapsed ? "collapsed" : ""}`}>
      <style>{`
        /* Chat panel: orange accent, subtle by default, stronger on hover/focus */
        .chat-panel {
          display: flex;
          flex-direction: column;
          height: 90vh;
          overflow: hidden;
          border-radius: 12px;
          border: 1.5px solid rgba(255,122,24,0.10); /* subtle default orange */
          box-shadow:
            inset 0 0 0 1px rgba(255,255,255,0.01),
            inset 0 8px 24px rgba(255,122,24,0.02),
            0 8px 28px rgba(0,0,0,0.45);
          transition: border-color .16s ease, box-shadow .18s ease, transform .12s ease;
          background: linear-gradient(180deg, rgba(255,255,255,0.005), rgba(255,255,255,0.01));
        }

        /* stronger accent when user interacts with the chat panel */
        .chat-panel:hover,
        .chat-panel:focus-within {
          border-color: rgba(255,122,24,0.36);
          box-shadow:
            inset 0 0 0 1px rgba(255,255,255,0.01),
            inset 0 18px 48px rgba(255,122,24,0.06),
            0 14px 42px rgba(0,0,0,0.50);
        }

        /* ensure the header/footer sit flush with panel edges */
        .chat-panel .header {
          border-radius: 12px 12px 0 0;
          background: transparent;
        }
        .chat-panel .footer {
          border-radius: 0 0 12px 12px;
          background: transparent;
          border-top: 1px solid rgba(255,255,255,0.03);
        }

        /* inner layout rules */
        .chat-panel .content {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }
        .chat-panel .chat-scroll {
          flex: 1;
          overflow-y: auto;
          padding: 16px 24px;
          scroll-behavior: smooth;
          background: transparent; /* let panel surface show */
        }

        /* keep ShinyText area visually separated */
        .chat-panel .shiny-wrap { padding: 10px 20px; }

        /* footer visual polish */
        .chat-panel .footer {
          position: sticky;
          bottom: 0;
          padding: 12px 24px;
          z-index: 5;
        }

        /* keyboard accessibility: visible ring when focusing input inside panel */
        .chat-panel:focus-within {
          outline: none;
          box-shadow:
            inset 0 0 0 1px rgba(255,255,255,0.01),
            0 0 0 4px rgba(255,122,24,0.06);
        }

        /* small screens - reduce height slightly */
        @media (max-width: 900px) {
          .chat-panel { height: calc(100vh - 48px); }
        }
      `}</style>

      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed((x) => !x)} />

      {/* added chat-panel class so styles are scoped to chat area only */}
      <section className="main chat-panel">
        {!userHasSentMessage && (
          <div className="header">
            <div>
              <div style={{ fontWeight: 700, fontSize: "1.2rem" }}>
                Talk with Market
              </div>
              <div className="mini">
                Ask questions regarding market trends and it will be delivered to you instantly.
              </div>
            </div>
          </div>
        )}

        <div className="content">
          <div className="chat-scroll" ref={scrollRef}>
            {msgs.map((m, i) => (
              <ChatMessage
                key={i}
                role={m.role === "user" ? "user" : "bot"}
                text={m.text}
                timestamp={m.timestamp}
                userInitial={(user?.email?.[0] || "U").toUpperCase()}
                onEdit={(newText) => handleEdit(i, newText)}
              />
            ))}

            {loading && (
              <div className="shiny-wrap">
                <AITextLoading />
              </div>
            )}
          </div>

          {/* ✅ Sticky footer */}
          <div className="footer">
            <ChatInput
              onSend={handleSend}
              placeholder="e.g., What's the market sentiment today?"
              loading={loading}
            />
          </div>
        </div>
      </section>
    </div>
  );
}