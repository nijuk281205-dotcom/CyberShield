import { useState } from "react";
import { scan, errorMessage } from "../services/api";
import { ResultCard, Spinner } from "../components/Common";

const EXAMPLES = {
  url: "http://secure-login.paypal.account-verify.xyz/update?id=123",
  text: "URGENT: Your bank account will be suspended today. Share the OTP sent to your phone to avoid closure.",
};

export default function Scanner() {
  const [mode, setMode] = useState("url");
  const [value, setValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    if (!value.trim()) return setError(mode === "url" ? "Enter a URL to check." : "Paste a message to check.");
    setLoading(true); setError(""); setResult(null);
    try {
      setResult(await scan(mode, value));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const switchMode = (m) => { setMode(m); setValue(""); setError(""); setResult(null); };

  return (
    <>
      <header className="page-head">
        <h1>Check a link or message</h1>
        <p>Nothing you enter is opened or run. We only read the text for warning signs.</p>
      </header>

      <form className="card" onSubmit={submit}>
        <div className="tabs" role="tablist">
          <button type="button" role="tab" aria-selected={mode === "url"} className={mode === "url" ? "on" : ""} onClick={() => switchMode("url")}>Link</button>
          <button type="button" role="tab" aria-selected={mode === "text"} className={mode === "text" ? "on" : ""} onClick={() => switchMode("text")}>Message</button>
        </div>

        {mode === "url" ? (
          <input type="text" value={value} onChange={(e) => setValue(e.target.value)} maxLength={2048}
            placeholder="https://example.com/login" aria-label="URL to check" autoComplete="off" spellCheck="false" />
        ) : (
          <textarea rows={6} value={value} onChange={(e) => setValue(e.target.value)} maxLength={5000}
            placeholder="Paste an SMS, email or chat message" aria-label="Message to check" />
        )}

        <div className="row">
          <button className="btn primary" disabled={loading}>{loading ? "Checking…" : "Check now"}</button>
          <button type="button" className="btn ghost" onClick={() => setValue(EXAMPLES[mode])}>Try an example</button>
        </div>
        {error && <p className="alert error" role="alert">{error}</p>}
      </form>

      {loading && <Spinner label="Analyzing" />}
      {result && (
        <>
          <p className="alert success">Result saved to your history.</p>
          <ResultCard result={result} />
        </>
      )}
    </>
  );
}
