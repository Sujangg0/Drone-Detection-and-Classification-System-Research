import React, { useEffect, useMemo, useRef, useState } from "react";

/**
 * Single-file Dashboard in App.jsx
 * Backend endpoints (your FastAPI):
 *   POST  http://localhost:8000/start
 *   POST  http://localhost:8000/stop
 *   GET   http://localhost:8000/latest
 *   GET   http://localhost:8000/events?limit=20
 *   POST  http://localhost:8000/settings   { threshold }
 */

const API_BASE = "http://localhost:8000"; // ✅ backend port 8000

function fmtTs(ts) {
  if (!ts) return "-";
  const d = new Date(ts * 1000);
  return Number.isNaN(d.getTime()) ? String(ts) : d.toLocaleString();
}

export default function App() {
  const [latest, setLatest] = useState(null);
  const [events, setEvents] = useState([]);
  const [limit, setLimit] = useState(20);

  const [thresholdDraft, setThresholdDraft] = useState(0.5);
  const [thresholdServer, setThresholdServer] = useState(null);

  const [pollMs, setPollMs] = useState(800);

  const [statusMsg, setStatusMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const timerRef = useRef(null);

  async function api(path, opts = {}) {
    const url = `${API_BASE}${path}`;
    const res = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      ...opts,
    });
    const txt = await res.text();
    let data;
    try {
      data = txt ? JSON.parse(txt) : null;
    } catch {
      data = txt;
    }
    if (!res.ok) throw new Error((data && data.detail) || txt || `HTTP ${res.status}`);
    return data;
  }

  async function refreshLatest() {
    try {
      const data = await api("/latest");
      setLatest(data);
      if (data && typeof data.threshold === "number") {
        setThresholdServer(Number(data.threshold));
        setThresholdDraft((prev) => (thresholdServer == null ? Number(data.threshold) : prev));
      }
      setErrorMsg("");
    } catch (e) {
      setErrorMsg(String(e.message || e));
    }
  }

  async function refreshEvents() {
    try {
      const data = await api(`/events?limit=${encodeURIComponent(limit)}`);
      setEvents(Array.isArray(data) ? data : data?.events || []);
      setErrorMsg("");
    } catch (e) {
      setErrorMsg(String(e.message || e));
    }
  }

  async function startWorker() {
    try {
      const data = await api("/start", { method: "POST" });
      setStatusMsg(`Start: ${data.status || "ok"}`);
      setErrorMsg("");
      await refreshLatest();
      await refreshEvents();
    } catch (e) {
      setErrorMsg(`Start failed: ${String(e.message || e)}`);
    }
  }

  async function stopWorker() {
    try {
      const data = await api("/stop", { method: "POST" });
      setStatusMsg(`Stop: ${data.status || "ok"}`);
      setErrorMsg("");
    } catch (e) {
      setErrorMsg(`Stop failed: ${String(e.message || e)}`);
    }
  }

  async function applyThreshold() {
    try {
      const v = Number(thresholdDraft);
      if (!Number.isFinite(v)) throw new Error("Threshold must be a number");
      const data = await api("/settings", {
        method: "POST",
        body: JSON.stringify({ threshold: v }),
      });
      setThresholdServer(Number(data.threshold));
      setStatusMsg(`Threshold updated to ${Number(data.threshold).toFixed(3)}`);
      setErrorMsg("");
      await refreshLatest();
    } catch (e) {
      setErrorMsg(`Settings failed: ${String(e.message || e)}`);
    }
  }

  // Polling
  useEffect(() => {
    async function tick() {
      await refreshLatest();
      await refreshEvents();
    }
    tick();

    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(tick, Math.max(250, Number(pollMs) || 800));

    return () => timerRef.current && clearInterval(timerRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pollMs, limit]);

  const latestView = useMemo(() => {
    if (!latest) return { empty: true, msg: "No data yet" };
    if (latest.status === "no data yet") return { empty: true, msg: "No data yet (click Start)" };
    return {
      empty: false,
      label: latest.label ?? "-",
      pred: latest.pred ?? "-",
      confidence: typeof latest.confidence === "number" ? latest.confidence : null,
      detected: Boolean(latest.detected),
      latency: latest.latency_ms ?? null,
      ts: latest.timestamp ?? null,
      spec: Array.isArray(latest.spec_shape) ? latest.spec_shape.join(" × ") : "-",
      thr: typeof latest.threshold === "number" ? latest.threshold : thresholdServer,
    };
  }, [latest, thresholdServer]);

  // Minimal inline styles
  const box = {
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Arial",
    padding: 18,
    maxWidth: 1150,
    margin: "0 auto",
    color: "#0f172a",
  };
  const card = {
    background: "#fff",
    border: "1px solid #e2e8f0",
    borderRadius: 14,
    padding: 14,
    boxShadow: "0 1px 10px rgba(2,6,23,0.04)",
  };
  const btn = {
    border: "1px solid #cbd5e1",
    background: "#fff",
    padding: "8px 12px",
    borderRadius: 10,
    cursor: "pointer",
    fontWeight: 700,
  };
  const btnDark = { ...btn, background: "#0f172a", color: "#fff", borderColor: "#0f172a" };

  return (
    <div style={box}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "baseline" }}>
        <div>
          <div style={{ fontSize: 20, fontWeight: 900 }}>Drone RF Dashboard</div>
          <div style={{ color: "#64748b", fontSize: 12 }}>
            Backend: <code>{API_BASE}</code>
          </div>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button style={btnDark} onClick={startWorker}>Start</button>
          <button style={btn} onClick={stopWorker}>Stop</button>
        </div>
      </div>

      {(statusMsg || errorMsg) && (
        <div style={{ ...card, marginTop: 12, borderColor: errorMsg ? "#fecaca" : "#e2e8f0" }}>
          {statusMsg && <div style={{ fontWeight: 800 }}>{statusMsg}</div>}
          {errorMsg && <div style={{ marginTop: 6, color: "#b91c1c", fontWeight: 700 }}>{errorMsg}</div>}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: 14, marginTop: 14 }}>
        {/* Latest */}
        <div style={card}>
          <div style={{ fontWeight: 900 }}>Latest</div>

          {latestView.empty ? (
            <div style={{ marginTop: 10, color: "#64748b" }}>{latestView.msg}</div>
          ) : (
            <div style={{ marginTop: 10, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
              <div>
                <div style={{ color: "#64748b", fontSize: 12 }}>Label</div>
                <div style={{ fontSize: 22, fontWeight: 900, marginTop: 2 }}>
                  {latestView.label}{" "}
                  <span
                    style={{
                      marginLeft: 8,
                      padding: "2px 10px",
                      borderRadius: 999,
                      fontSize: 12,
                      fontWeight: 800,
                      border: "1px solid",
                      borderColor: latestView.detected ? "#fecaca" : "#cbd5e1",
                      background: latestView.detected ? "#fff1f2" : "#f8fafc",
                      color: latestView.detected ? "#b91c1c" : "#334155",
                    }}
                  >
                    {latestView.detected ? "DETECTED" : "NOISE"}
                  </span>
                </div>

                <div style={{ marginTop: 10, display: "flex", gap: 10, flexWrap: "wrap" }}>
                  <span style={{ fontSize: 12, padding: "2px 10px", border: "1px solid #e2e8f0", borderRadius: 999 }}>
                    pred: {latestView.pred}
                  </span>
                  <span style={{ fontSize: 12, padding: "2px 10px", border: "1px solid #e2e8f0", borderRadius: 999 }}>
                    conf: {latestView.confidence != null ? latestView.confidence.toFixed(3) : "-"}
                  </span>
                  <span style={{ fontSize: 12, padding: "2px 10px", border: "1px solid #e2e8f0", borderRadius: 999 }}>
                    latency: {latestView.latency != null ? `${Number(latestView.latency).toFixed(1)} ms` : "-"}
                  </span>
                </div>
              </div>

              <div>
                <div style={{ color: "#64748b", fontSize: 12 }}>Time</div>
                <div style={{ fontWeight: 800, marginTop: 2 }}>{fmtTs(latestView.ts)}</div>

                <div style={{ marginTop: 10, color: "#64748b", fontSize: 12 }}>Spectrogram</div>
                <div style={{ fontWeight: 800, marginTop: 2 }}>{latestView.spec}</div>

                <div style={{ marginTop: 10, color: "#64748b", fontSize: 12 }}>Threshold (server)</div>
                <div style={{ fontWeight: 900, marginTop: 2 }}>
                  {latestView.thr != null ? Number(latestView.thr).toFixed(3) : "-"}
                </div>
              </div>
            </div>
          )}

          {/* Settings */}
          <div style={{ marginTop: 14, borderTop: "1px solid #e2e8f0", paddingTop: 12 }}>
            <div style={{ fontWeight: 900 }}>Settings</div>

            <div style={{ marginTop: 10, display: "grid", gridTemplateColumns: "1fr 160px", gap: 10 }}>
              <div>
                <div style={{ color: "#64748b", fontSize: 12 }}>Threshold</div>
                <input
                  type="number"
                  step="0.001"
                  min="0"
                  max="1"
                  value={thresholdDraft}
                  onChange={(e) => setThresholdDraft(e.target.value)}
                  style={{
                    marginTop: 6,
                    width: "100%",
                    padding: "8px 10px",
                    borderRadius: 10,
                    border: "1px solid #cbd5e1",
                    outline: "none",
                  }}
                />
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.001"
                  value={thresholdDraft}
                  onChange={(e) => setThresholdDraft(e.target.value)}
                  style={{ width: "100%", marginTop: 8 }}
                />
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: 10, justifyContent: "flex-end" }}>
                <button style={btnDark} onClick={applyThreshold}>Apply</button>
                <button style={btn} onClick={() => { refreshLatest(); refreshEvents(); }}>Refresh</button>
              </div>
            </div>

            <div style={{ marginTop: 12, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
              <div>
                <div style={{ color: "#64748b", fontSize: 12 }}>Poll interval (ms)</div>
                <input
                  type="number"
                  min="250"
                  step="50"
                  value={pollMs}
                  onChange={(e) => setPollMs(e.target.value)}
                  style={{
                    marginTop: 6,
                    width: "100%",
                    padding: "8px 10px",
                    borderRadius: 10,
                    border: "1px solid #cbd5e1",
                  }}
                />
              </div>
              <div>
                <div style={{ color: "#64748b", fontSize: 12 }}>Events limit</div>
                <input
                  type="number"
                  min="1"
                  max="500"
                  value={limit}
                  onChange={(e) => setLimit(Number(e.target.value || 20))}
                  style={{
                    marginTop: 6,
                    width: "100%",
                    padding: "8px 10px",
                    borderRadius: 10,
                    border: "1px solid #cbd5e1",
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Events */}
        <div style={card}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
            <div style={{ fontWeight: 900 }}>Events</div>
            <button style={btn} onClick={refreshEvents}>Refresh</button>
          </div>

          <div style={{ marginTop: 12, maxHeight: 520, overflow: "auto", border: "1px solid #e2e8f0", borderRadius: 12 }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ background: "#f8fafc" }}>
                  <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Time</th>
                  <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Label</th>
                  <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Conf</th>
                  <th style={{ textAlign: "left", padding: 10, borderBottom: "1px solid #e2e8f0" }}>Latency</th>
                </tr>
              </thead>
              <tbody>
                {events.length === 0 ? (
                  <tr>
                    <td colSpan={4} style={{ padding: 12, color: "#64748b" }}>
                      No detection events yet. Click <b>Start</b> and wait.
                    </td>
                  </tr>
                ) : (
                  events.map((ev, idx) => (
                    <tr key={idx} style={{ background: idx % 2 ? "#fff" : "#fbfdff" }}>
                      <td style={{ padding: 10, borderBottom: "1px solid #f1f5f9", whiteSpace: "nowrap" }}>
                        {fmtTs(ev.timestamp)}
                      </td>
                      <td style={{ padding: 10, borderBottom: "1px solid #f1f5f9" }}>{ev.label ?? "-"}</td>
                      <td style={{ padding: 10, borderBottom: "1px solid #f1f5f9" }}>
                        {typeof ev.confidence === "number" ? ev.confidence.toFixed(3) : "-"}
                      </td>
                      <td style={{ padding: 10, borderBottom: "1px solid #f1f5f9" }}>
                        {ev.latency_ms != null ? `${Number(ev.latency_ms).toFixed(1)} ms` : "-"}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: 10, color: "#64748b", fontSize: 12 }}>
            Tip: If Latest stays “no data yet”, run backend start:{" "}
            <code>curl -X POST http://localhost:8000/start</code>
          </div>
        </div>
      </div>
    </div>
  );
}
