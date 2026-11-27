import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getStats, errorMessage } from "../services/api";
import { RiskBadge, Spinner, formatDate } from "../components/Common";

function Daily({ daily }) {
  const days = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date(); d.setUTCDate(d.getUTCDate() - i);
    const key = d.toISOString().slice(0, 10);
    days.push({ key, label: d.toLocaleDateString(undefined, { weekday: "short", timeZone: "UTC" }), count: daily.find((x) => x.date === key)?.count || 0 });
  }
  const max = Math.max(...days.map((d) => d.count), 1);
  return (
    <div className="bars" role="img" aria-label="Scans per day, last 7 days">
      {days.map((d) => (
        <div key={d.key} className="bar-col">
          <span className="bar-n">{d.count}</span>
          <div className="bar" style={{ height: `${(d.count / max) * 100}%` }} />
          <span className="bar-l">{d.label}</span>
        </div>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getStats().then(setStats).catch((e) => setError(errorMessage(e)));
  }, []);

  if (error) return <p className="alert error" role="alert">{error}</p>;
  if (!stats) return <Spinner />;

  const { total, by_risk: r } = stats;
  const pct = (n) => (total ? Math.round((n / total) * 100) : 0);
  const hi = pct(r.High), me = pct(r.Medium);
  const donut = total
    ? `conic-gradient(var(--high) 0 ${hi}%, var(--medium) ${hi}% ${hi + me}%, var(--low) ${hi + me}% 100%)`
    : "conic-gradient(var(--line) 0 100%)";

  return (
    <>
      <header className="page-head">
        <h1>Overview</h1>
        <p>Live numbers from every check saved on this server.</p>
      </header>

      <div className="stats">
        <div className="card stat"><span>Total checks</span><strong>{total}</strong></div>
        <div className="card stat high"><span>High risk</span><strong>{r.High}</strong></div>
        <div className="card stat medium"><span>Medium risk</span><strong>{r.Medium}</strong></div>
        <div className="card stat low"><span>Low risk</span><strong>{r.Low}</strong></div>
      </div>

      <div className="grid2">
        <section className="card">
          <h2>Checks in the last 7 days</h2>
          <Daily daily={stats.daily} />
        </section>
        <section className="card">
          <h2>Risk split</h2>
          <div className="donut-wrap">
            <div className="donut" style={{ background: donut }}><div>{total}</div></div>
            <ul className="legend">
              <li><i className="d high" />High {r.High}</li>
              <li><i className="d medium" />Medium {r.Medium}</li>
              <li><i className="d low" />Low {r.Low}</li>
              <li className="muted">Links {stats.by_kind.url} · Messages {stats.by_kind.text}</li>
            </ul>
          </div>
        </section>
      </div>

      <section className="card">
        <div className="row between">
          <h2>Recent activity</h2>
          <Link to="/history" className="link">View all history</Link>
        </div>
        {stats.recent.length === 0 ? (
          <div className="empty"><p>No checks yet.</p><Link className="btn primary" to="/scan">Run your first check</Link></div>
        ) : (
          <ul className="recent">
            {stats.recent.map((s) => (
              <li key={s.id}>
                <div className="grow"><span className="clip">{s.input}</span><small>{s.kind === "url" ? "Link" : "Message"} · {formatDate(s.created_at)}</small></div>
                <RiskBadge level={s.risk_level} />
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
