import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import { getIndicesSnapshot } from "../services/marketApi"; // your existing fn

const MarketCtx = createContext(null);
export const useMarket = () => useContext(MarketCtx);

/** App-wide market provider with continuous polling */
export function MarketProvider({ children, refreshMs = 15000 }) {
  const [data, setData] = useState(null); // { nifty:{price,pct}, sensex:{price,pct}, ts }
  const [error, setError] = useState(null);
  const timerRef = useRef(null);

  const pull = async () => {
    try {
      const snap = await getIndicesSnapshot();
      setData(snap);
      setError(null);
    } catch (e) {
      setError(e?.message || "Market feed error");
    }
  };

  useEffect(() => {
    // initial fetch
    pull();
    // continuous polling
    timerRef.current = setInterval(pull, refreshMs);

    // throttle when tab is hidden to save CPU/network
    const onVisibility = () => {
      if (document.hidden) {
        clearInterval(timerRef.current);
        timerRef.current = setInterval(pull, Math.max(refreshMs * 3, 45000));
      } else {
        clearInterval(timerRef.current);
        pull();
        timerRef.current = setInterval(pull, refreshMs);
      }
    };
    document.addEventListener("visibilitychange", onVisibility);

    return () => {
      document.removeEventListener("visibilitychange", onVisibility);
      clearInterval(timerRef.current);
    };
  }, [refreshMs]);

  const value = { data, error, refresh: pull };
  return <MarketCtx.Provider value={value}>{children}</MarketCtx.Provider>;
}
