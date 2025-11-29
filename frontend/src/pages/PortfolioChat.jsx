import React, { useEffect, useRef, useState } from "react";
import Sidebar from "../components/Sidebar";
import ChatInput from "../components/ChatInput";
import ChatMessage from "../components/ChatMessage";
import { useAuth } from "../auth";
import { Navigate } from "react-router-dom";
import ShinyText from "../components/ShinyText";
import "../components/ShinyText.css";
import { portfolioChatbotStream } from "../services/api";

export default function PortfolioChat() {
  const { user } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [msgs, setMsgs] = useState([
    {
      role: "bot",
      text: "I can answer questions using your portfolio data.",
      timestamp: new Date(),
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [authError, setAuthError] = useState(null);
  const scrollRef = useRef(null);
  const hasInitialized = useRef(false);

  const userHasSentMessage = msgs.some((m) => m.role === "user");

  // scroll helper: wait a tick so layout/transition finishes, then scroll
  const scrollToBottom = () => {
    // small delay to allow header collapse/DOM updates to finish
    setTimeout(() => {
      requestAnimationFrame(() => {
        if (scrollRef.current) {
          scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
      });
    }, 50);
  };

  useEffect(() => {
    // whenever messages, loading, or header state changes -> scroll
    scrollToBottom();
  }, [msgs, loading, userHasSentMessage]);

  // Initialize portfolio connection on component mount (triggers Kite login)
  useEffect(() => {
    if (!user || hasInitialized.current) return;

    hasInitialized.current = true;

    const initializePortfolio = async () => {
      setInitializing(true);
      setAuthError(null);

      try {
        // Send an initialization query to trigger Kite authentication
        await portfolioChatbotStream(
          "initialize", // Dummy query to trigger auth
          () => { }, // onChunk - ignore chunks during initialization
          () => {
            // onComplete
            console.log("Portfolio initialized successfully");
            setInitializing(false);
            setMsgs((m) => [
              ...m,
              {
                role: "bot",
                text: "Portfolio connected! You can now ask questions about your holdings, P/L, and more.",
                timestamp: new Date(),
              }
            ]);
          },
          (error) => {
            // onError
            console.error("Portfolio initialization error:", error);
            setInitializing(false);
            setAuthError(error.message);
            setMsgs((m) => [
              ...m,
              {
                role: "bot",
                text: "Failed to connect to your portfolio. Please make sure you're logged in to Kite.",
                timestamp: new Date(),
              }
            ]);
          }
        );
      } catch (error) {
        console.error("Portfolio initialization error:", error);
        setInitializing(false);
        setAuthError(error.message);
      }
    };

    initializePortfolio();
  }, [user]);

  if (!user) return <Navigate to="/login" replace />;

  const handleSend = async (q) => {
    // add user message immediately for snappy UI
    setMsgs((m) => [...m, { role: "user", text: q, timestamp: new Date() }]);
    setLoading(true);

    let botResponse = "";

    try {
      // Use streaming endpoint for chat
      await portfolioChatbotStream(
        q,
        (chunk) => {
          // onChunk - accumulate response
          botResponse += chunk;
          // Update the last bot message in real-time
          setMsgs((m) => {
            const newMsgs = [...m];
            const lastMsg = newMsgs[newMsgs.length - 1];
            if (lastMsg && lastMsg.role === "bot" && lastMsg.streaming) {
              lastMsg.text = botResponse;
            } else {
              newMsgs.push({
                role: "bot",
                text: botResponse,
                timestamp: new Date(),
                streaming: true,
              });
            }
            return newMsgs;
          });
        },
        () => {
          // onComplete
          setLoading(false);
          // Mark streaming as complete
          setMsgs((m) => {
            const newMsgs = [...m];
            const lastMsg = newMsgs[newMsgs.length - 1];
            if (lastMsg && lastMsg.streaming) {
              delete lastMsg.streaming;
            }
            return newMsgs;
          });
        },
        (error) => {
          // onError
          console.error("Portfolio chatbot error:", error);
          setLoading(false);
          const friendly = `Sorry, something went wrong while contacting the portfolio assistant. ${error.message ? `(${error.message})` : ""}`;
          setMsgs((m) => [...m, { role: "bot", text: friendly, timestamp: new Date() }]);
        }
      );
    } catch (e) {
      console.error("Portfolio chatbot error:", e);
      setLoading(false);
      const friendly = `Sorry, something went wrong while contacting the portfolio assistant. ${e.message ? `(${e.message})` : ""}`;
      setMsgs((m) => [...m, { role: "bot", text: friendly, timestamp: new Date() }]);
    }
  };

  const handleEdit = async (index, newText) => {
    // Keep messages up to the edited one, and update the edited message
    const newMsgs = msgs.slice(0, index + 1);
    newMsgs[index] = { ...newMsgs[index], text: newText, timestamp: new Date() };
    setMsgs(newMsgs);

    setLoading(true);
    let botResponse = "";

    try {
      await portfolioChatbotStream(
        newText,
        (chunk) => {
          botResponse += chunk;
          setMsgs((m) => {
            const newMsgs = [...m];
            const lastMsg = newMsgs[newMsgs.length - 1];
            if (lastMsg && lastMsg.role === "bot" && lastMsg.streaming) {
              lastMsg.text = botResponse;
            } else {
              newMsgs.push({
                role: "bot",
                text: botResponse,
                timestamp: new Date(),
                streaming: true,
              });
            }
            return newMsgs;
          });
        },
        () => {
          setLoading(false);
          setMsgs((m) => {
            const newMsgs = [...m];
            const lastMsg = newMsgs[newMsgs.length - 1];
            if (lastMsg && lastMsg.streaming) {
              delete lastMsg.streaming;
            }
            return newMsgs;
          });
        },
        (error) => {
          console.error("Portfolio chatbot error:", error);
          setLoading(false);
          const friendly = `Sorry, something went wrong. ${error.message ? `(${error.message})` : ""}`;
          setMsgs((m) => [...m, { role: "bot", text: friendly, timestamp: new Date() }]);
        }
      );
    } catch (e) {
      console.error("Portfolio chatbot error:", e);
      setLoading(false);
      const friendly = `Sorry, something went wrong. ${e.message ? `(${e.message})` : ""}`;
      setMsgs((m) => [...m, { role: "bot", text: friendly, timestamp: new Date() }]);
    }
  };

  return (
    <div className={`app-shell ${collapsed ? "collapsed" : ""}`}>
      <style>{`
        .main {
          display: flex;
          flex-direction: column;
          height: 90vh;
          overflow: hidden;
        }
        .content {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        /* Header: normal height -> collapsed to 0 with transition */
        .header {
          height: 72px;             /* visible header height */
          display: flex;
          align-items: center;
          padding: 12px 24px;
          box-sizing: border-box;
          transition: height 180ms ease, padding 180ms ease, opacity 150ms ease;
          overflow: hidden;         /* required for height collapse */
          opacity: 1;
        }
        .header.collapsed {
          height: 0;                /* collapses the space */
          padding-top: 0;
          padding-bottom: 0;
          opacity: 0;
        }

        /* Chat scroll: keep bottom padding so messages aren't obscured by footer */
        .chat-scroll {
          flex: 1;
          overflow-y: auto;
          padding: 16px 24px;
          padding-bottom: 20px; /* reduced padding to curb the gap */
          scroll-behavior: smooth;
          box-sizing: border-box;
        }

        /* Footer remains sticky and unchanged */
        .footer {
          position: sticky;
          bottom: 0;
          background: #0d1117;
          padding: 12px 24px;
          border-top: 1px solid rgba(255,255,255,0.1);
          z-index: 5;
        }

        /* Optional small helpers */
        .mini { color: rgba(255,255,255,0.75); }
        
        /* Initializing overlay */
        .initializing-overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(13, 17, 23, 0.95);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          flex-direction: column;
          gap: 16px;
        }
      `}</style>

      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed((x) => !x)} />

      <section className="main">
        {/* Show initializing overlay */}
        {initializing && (
          <div className="initializing-overlay">
            <ShinyText
              text="Connecting to your portfolio..."
              disabled={false}
              speed={3}
              className="custom-class"
            />
            <div style={{ color: "rgba(255,255,255,0.6)", fontSize: "0.9rem" }}>
              You may be redirected to Kite for authentication
            </div>
          </div>
        )}

        {/* Render header and toggle collapsed class so header height actually becomes 0 */}
        <div className={`header ${userHasSentMessage ? "collapsed" : ""}`}>
          <div>
            <div style={{ fontWeight: 700, fontSize: "1.2rem" }}>
              Talk with Portfolio
            </div>
            <div className="mini">
              Ask about P/L, sector exposure, risk, and more.
              {authError && (
                <span style={{ color: "#ff6b6b", marginLeft: "8px" }}>
                  (Authentication required)
                </span>
              )}
            </div>
          </div>
        </div>

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
              <div style={{ padding: "10px 20px" }}>
                <ShinyText
                  text="Thinking..."
                  disabled={false}
                  speed={3}
                  className="custom-class"
                />
              </div>
            )}
          </div>

          <div className="footer">
            <ChatInput
              onSend={handleSend}
              placeholder="e.g., Show unrealized P/L by sector for last 30 days"
              loading={loading || initializing}
            />
          </div>
        </div>
      </section>
    </div>
  );
}
