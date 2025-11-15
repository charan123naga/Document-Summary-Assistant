import { useState } from "react";
import { uploadFile, summarizeText } from "./services/api";

export default function App() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [summary, setSummary] = useState("");
  const [points, setPoints] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [theme, setTheme] = useState(() => {
    if (typeof window === "undefined") return "light";
    return localStorage.getItem("theme") || "light";
  });
  const [copied, setCopied] = useState(false);

  if (typeof document !== "undefined") {
    document.documentElement.setAttribute("data-theme", theme);
  }

  const onUpload = async () => {
    if (!file) return setError("Please choose a file first.");
    setError("");
    setLoading(true);
    try {
      const res = await uploadFile(file);
      setText(res.text || "");
    } catch (e) {
      setError(e.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const onSummarize = async (level) => {
    if (!text) return setError("No text to summarize.");
    setError("");
    setLoading(true);
    try {
      const res = await summarizeText(text, level);
      setSummary(res.summary || "");
      setPoints(res.points || []);
      setSuggestions(res.suggestions || []);
    } catch (e) {
      setError(e.message || "Summarization failed");
    } finally {
      setLoading(false);
    }
  };

  const toggleTheme = () => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    localStorage.setItem("theme", next);
  };

  const copySummary = async () => {
    try {
      await navigator.clipboard.writeText(summary || "");
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch (e) {
      setError("Could not copy to clipboard");
    }
  };

  return (
    <main>
      <h1>Document Summarizer</h1>
      <p className="subtitle">
        Upload a PDF, extract text, and get a concise summary.
      </p>

      <div className="toolbar">
        <span className="chip">Theme</span>
        <button onClick={toggleTheme}>
          {theme === "light" ? "Dark" : "Light"} mode
        </button>
      </div>

      <section>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <button className="primary" onClick={onUpload} disabled={loading}>
          Upload & Extract
        </button>
      </section>

      {error && <div className="error">{error}</div>}
      {loading && (
        <div className="loading">
          <span className="spinner" />
          Processing…
        </div>
      )}

      <div className="row">
        <section>
          <h2>Extracted Text</h2>
          <textarea
            rows={16}
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </section>

        <section>
          <h2>Summary</h2>
          <div className="controls">
            <button onClick={() => onSummarize("short")} disabled={loading}>
              Short
            </button>
            <button onClick={() => onSummarize("medium")} disabled={loading}>
              Medium
            </button>
            <button onClick={() => onSummarize("long")} disabled={loading}>
              Long
            </button>
            <button onClick={copySummary} disabled={!summary}>
              {copied ? "Copied!" : "Copy summary"}
            </button>
          </div>
          <pre className="summary">{summary}</pre>

          {points.length > 0 && (
            <div className="points">
              <h3>Key Points</h3>
              <ul>
                {points.map((p, i) => (
                  <li key={i}>{p}</li>
                ))}
              </ul>
            </div>
          )}

          {suggestions.length > 0 && (
            <div className="suggestions">
              <h3>Improvement Suggestions</h3>
              <ul>
                {suggestions.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
