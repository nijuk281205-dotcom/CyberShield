import { useCallback, useEffect, useState } from "react";
import { getHistory, deleteScan, clearHistory, errorMessage } from "../services/api";
import { RiskBadge, Spinner, formatDate, Icon } from "../components/Common";

export default function History() {
  const [filters, setFilters] = useState({ search: "", risk: "", type: "" });
  const [query, setQuery] = useState(filters);
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [open, setOpen] = useState(null);

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      setData(await getHistory({ ...query, page, per_page: 10 }));
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setLoading(false);
    }
  }, [query, page]);

  useEffect(() => { load(); }, [load]);

  // debounce the search box
  useEffect(() => {
    const t = setTimeout(() => { setQuery(filters); setPage(1); }, 300);
    return () => clearTimeout(t);
  }, [filters]);

  const remove = async (id) => {
    if (!window.confirm("Delete this record?")) return;
    try { await deleteScan(id); setNotice("Record deleted."); load(); } catch (e) { setError(errorMessage(e)); }
  };
  const clearAll = async () => {
    if (!window.confirm("Delete ALL history? This can't be undone.")) return;
    try { const r = await clearHistory(); setNotice(`Deleted ${r.deleted} records.`); setPage(1); load(); } catch (e) { setError(errorMessage(e)); }
  };

  return (
    <>
      <header className="page-head">
        <h1>History</h1>
        <p>Every check is stored in the database and stays after a restart.</p>
      </header>

      <div className="card filters">
        <input type="search" placeholder="Search links or messages" aria-label="Search history" value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })} />
        <select aria-label="Filter by risk" value={filters.risk} onChange={(e) => setFilters({ ...filters, risk: e.target.value })}>
          <option value="">All risk levels</option><option>High</option><option>Medium</option><option>Low</option>
        </select>
        <select aria-label="Filter by type" value={filters.type} onChange={(e) => setFilters({ ...filters, type: e.target.value })}>
          <option value="">Links and messages</option><option value="url">Links</option><option value="text">Messages</option>
        </select>
        <button className="btn danger" onClick={clearAll} disabled={!data?.total}>Clear all</button>
      </div>

      {notice && <p className="alert success" role="status">{notice}</p>}
      {error && <p className="alert error" role="alert">{error}</p>}
      {loading && !data && <Spinner />}

      {data && (
        <section className="card">
          {data.items.length === 0 ? (
            <div className="empty"><p>No records match.</p></div>
          ) : (
            <ul className="recent">
              {data.items.map((s) => (
                <li key={s.id} className="hist">
                  <div className="row between">
                    <div className="grow">
                      <button className="linkbtn clip" onClick={() => setOpen(open === s.id ? null : s.id)} aria-expanded={open === s.id}>{s.input}</button>
                      <small>{s.kind === "url" ? "Link" : "Message"} · {formatDate(s.created_at)} · score {s.score}</small>
                    </div>
                    <RiskBadge level={s.risk_level} />
                    <button className="icon-btn" onClick={() => remove(s.id)} aria-label="Delete record"><Icon name="trash" /></button>
                  </div>
                  {open === s.id && (
                    <div className="detail">
                      <p>{s.summary}</p>
                      <ul>{s.findings.map((f, i) => <li key={i}><strong>{f.title}</strong> (+{f.points}): {f.detail}</li>)}</ul>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          )}
          <div className="pager">
            <button className="btn ghost" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>
            <span>Page {data.page} of {data.pages} · {data.total} records</span>
            <button className="btn ghost" disabled={page >= data.pages} onClick={() => setPage(page + 1)}>Next</button>
          </div>
        </section>
      )}
    </>
  );
}
