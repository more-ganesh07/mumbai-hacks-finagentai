// "use client";

// import { Mic } from "lucide-react";
// import { useState, useEffect, useRef } from "react";
// import "./AI_Voice.css";

// /**
//  * Props:
//  *  - onTranscript(text: string) => void
//  *  - onListeningChange(isListening: boolean) => void
//  *  - autoSendOnStop (boolean) optional
//  */
// export default function AI_Voice({ onTranscript = () => {}, onListeningChange = () => {}, autoSendOnStop = false }) {
//   const [submitted, setSubmitted] = useState(false); // 'listening' state
//   const [time, setTime] = useState(0);
//   const [isClient, setIsClient] = useState(false);
//   const [isDemo, setIsDemo] = useState(false);
//   const recognitionRef = useRef(null);
//   const finalTranscriptRef = useRef("");

//   useEffect(() => setIsClient(true), []);

//   // timer while listening
//   useEffect(() => {
//     let intervalId;
//     if (submitted) {
//       intervalId = setInterval(() => setTime((t) => t + 1), 1000);
//     } else {
//       setTime(0);
//     }
//     return () => clearInterval(intervalId);
//   }, [submitted]);

//   const formatTime = (seconds) => {
//     const mins = Math.floor(seconds / 60);
//     const secs = seconds % 60;
//     return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
//   };

//   // Setup Web Speech API (if available)
//   useEffect(() => {
//     const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
//     if (!SpeechRecognition) {
//       setIsDemo(true);
//       return;
//     }

//     const r = new SpeechRecognition();
//     r.lang = "en-US";
//     r.interimResults = true;
//     r.continuous = false;
//     recognitionRef.current = r;

//     r.onstart = () => {
//       finalTranscriptRef.current = "";
//       setSubmitted(true);
//       onListeningChange(true);
//     };

//     r.onresult = (event) => {
//       let interim = "";
//       let final = "";
//       for (let i = event.resultIndex; i < event.results.length; i++) {
//         const res = event.results[i];
//         if (res.isFinal) final += res[0].transcript;
//         else interim += res[0].transcript;
//       }
//       if (final) {
//         finalTranscriptRef.current += final;
//         onTranscript(finalTranscriptRef.current.trim());
//       } else {
//         onTranscript((finalTranscriptRef.current + " " + interim).trim());
//       }
//     };

//     r.onerror = (e) => {
//       console.warn("SpeechRecognition error", e);
//       setIsDemo(true);
//       setSubmitted(false);
//       onListeningChange(false);
//     };

//     r.onend = () => {
//       setSubmitted(false);
//       onListeningChange(false);
//       if (finalTranscriptRef.current) {
//         onTranscript(finalTranscriptRef.current.trim());
//         if (autoSendOnStop) {
//           // parent handles sending if desired via onTranscript + listening change
//         }
//       }
//     };

//     return () => {
//       try {
//         r.onstart = null;
//         r.onresult = null;
//         r.onend = null;
//         r.onerror = null;
//         r.stop && r.stop();
//       } catch {}
//     };
//   }, [onTranscript, onListeningChange, autoSendOnStop]);

//   // Demo animation runner
//   useEffect(() => {
//     if (!isDemo) return;
//     let timeoutId;
//     const runAnimation = () => {
//       setSubmitted(true);
//       timeoutId = setTimeout(() => {
//         setSubmitted(false);
//         timeoutId = setTimeout(runAnimation, 1000);
//       }, 3000);
//     };
//     const initialTimeout = setTimeout(runAnimation, 100);
//     return () => {
//       clearTimeout(timeoutId);
//       clearTimeout(initialTimeout);
//     };
//   }, [isDemo]);

//   const startRecognition = () => {
//     const r = recognitionRef.current;
//     if (r) {
//       try {
//         r.start();
//       } catch (e) {
//         console.debug("recognition start failed", e);
//       }
//     } else {
//       setIsDemo(true);
//       setSubmitted(true);
//       onListeningChange(true);
//       setTimeout(() => {
//         const fake = "This is a demo transcription.";
//         onTranscript(fake);
//         setSubmitted(false);
//         onListeningChange(false);
//       }, 3000);
//     }
//   };

//   const stopRecognition = () => {
//     const r = recognitionRef.current;
//     if (r) {
//       try {
//         r.stop();
//       } catch {}
//     } else {
//       setSubmitted(false);
//       onListeningChange(false);
//     }
//   };

//   const handleClick = () => {
//     if (submitted) {
//       stopRecognition();
//     } else {
//       finalTranscriptRef.current = "";
//       startRecognition();
//     }
//   };

//   return (
//     <div className="ai-voice">
//       <div className="ai-voice__inner">
//         <button
//           className={`ai-voice__button ${submitted ? "ai-voice__button--active" : ""}`}
//           type="button"
//           onClick={handleClick}
//           aria-pressed={submitted}
//           aria-label={submitted ? "Stop listening" : "Start voice input"}
//         >
//           {submitted ? (
//             <div className="ai-voice__spinner" aria-hidden="true" />
//           ) : (
//             <Mic className="ai-voice__mic" />
//           )}
//         </button>

//         <span className={`ai-voice__time ${submitted ? "ai-voice__time--active" : ""}`}>
//           {formatTime(time)}
//         </span>

//         <div className="ai-voice__bars" aria-hidden="true">
//           {[...Array(32)].map((_, i) => {
//             const style = submitted && isClient ? { height: `${8 + Math.random() * 72}%`, animationDelay: `${i * 0.04}s` } : {};
//             return <div key={i} className={`ai-voice__bar ${submitted ? "ai-voice__bar--active" : ""}`} style={style} />;
//           })}
//         </div>

//         <p className="ai-voice__caption">{submitted ? "Listening..." : "Click to speak"}</p>
//       </div>
//     </div>
//   );
// }


"use client";

import { Mic } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import "./AI_Voice.css";

/**
 * Small, plain-CSS mic button component.
 * Props:
 *  - variant: "button" (default) | "panel" (not used now)
 *  - disabled: boolean (if true, button is disabled and shows tooltip)
 *  - onTranscript / onListeningChange left for future use but won't be triggered when disabled
 */
export default function AI_Voice({
  variant = "button",
  disabled = false,
  onTranscript = () => {},
  onListeningChange = () => {},
}) {
  // keep internal state minimal — we won't start recognition while disabled
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    // set up recognition only for future use; we won't start it while disabled
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
    if (!SpeechRecognition) return;
    const r = new SpeechRecognition();
    r.lang = "en-US";
    r.interimResults = true;
    r.continuous = false;
    recognitionRef.current = r;

    r.onstart = () => { setListening(true); onListeningChange(true); };
    r.onend = () => { setListening(false); onListeningChange(false); };
    r.onresult = (e) => {
      let interim = "", final = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const res = e.results[i];
        if (res.isFinal) final += res[0].transcript;
        else interim += res[0].transcript;
      }
      if (final) onTranscript(final.trim());
      else onTranscript(interim.trim());
    };

    return () => {
      try {
        r.onstart = r.onend = r.onresult = null;
        r.stop && r.stop();
      } catch {}
    };
  }, [onTranscript, onListeningChange]);

  const handleClick = () => {
    // If disabled, do nothing.
    if (disabled) return;
    // For now, keep the toggle minimal (no animation). This is placeholder for future behavior.
    if (listening && recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch {}
    } else if (recognitionRef.current) {
      try { recognitionRef.current.start(); } catch {}
    } else {
      // No speech API — could open "coming soon" flow in future.
    }
  };

  // only rendering the compact button variant (as requested)
  return (
    <span className="ai-voice-tooltip" data-tooltip={disabled ? "Voice feature coming soon" : ""}>
      <button
        className={`ai-voice-btn ${disabled ? "ai-voice-btn--disabled" : ""}`}
        type="button"
        onClick={handleClick}
        aria-pressed={listening}
        aria-label={disabled ? "Voice (coming soon)" : (listening ? "Stop listening" : "Start voice input")}
        disabled={disabled}
      >
        <Mic className="mic-icon" />
      </button>
    </span>
  );
}
