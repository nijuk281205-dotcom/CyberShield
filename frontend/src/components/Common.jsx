export const Icon = ({ name }) => {
  const p = {
    dashboard: "M3 3h8v8H3zM13 3h8v5h-8zM13 10h8v11h-8zM3 13h8v8H3z",
    scan: "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM21 21l-5-5",
    history: "M3 12a9 9 0 1 0 3-6.700M3 4v5h5M12 7v5l3 2",
    info: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 11v5M12 8h.01",
    menu: "M4 6h16M4 12h16M4 18h16",
    trash: "M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13",
  }[name];
  return (
    <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d={p} />
    </svg>
  );
};

export const Logo = () => (
  <div className="logo">
    <svg viewBox="0 0 32 32" width="28" height="28" aria-hidden="true">
      <path d="M16 2 4 7v8c0 7.500 5 13 12 15 7-2 12-7.500 12-15V7z" fill="#5B8CFF" />
      <path d="m10.500 16 4 4 7-8" stroke="#fff" strokeWidth="3" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
    <span>CyberShield</span>
  </div>
);

export const RiskBadge = ({ level }) => <span className={`badge ${level.toLowerCase()}`}>{level} risk</span>;

export const Spinner = ({ label = "Loading" }) => (
  <div className="spinner-wrap" role="status">
    <div className="spinner" />
    <span>{label}…</span>
  </div>
);

export const formatDate = (iso) =>
  new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });

export function ResultCard({ result }) {
  const lvl = result.risk_level.toLowerCase();
  return (
    <section className={`card result ${lvl}`} aria-live="polite">
      <div className="result-head">
        <div>
          <RiskBadge level={result.risk_level} />
          <p className="result-summary">{result.summary}</p>
        </div>
        <div className="score">
          <strong>{result.score}</strong>
          <span>/ 100 risk score</span>
        </div>
      </div>
      <div className="meter"><div style={{ width: `${result.score}%` }} /></div>

      <h3>Why this result</h3>
      {result.findings.length === 0 ? (
        <p className="muted">No indicators matched our rules.</p>
      ) : (
        <ul className="findings">
          {result.findings.map((f, i) => (
            <li key={i}>
              <div><strong>{f.title}</strong><p>{f.detail}</p></div>
              <span className="pts">+{f.points}</span>
            </li>
          ))}
        </ul>
      )}

      <h3>What to do</h3>
      <ul className="recs">{result.recommendations.map((r, i) => <li key={i}>{r}</li>)}</ul>

      {result.limitations && <p className="limits"><strong>Limits of this check.</strong> {result.limitations}</p>}
    </section>
  );
}
