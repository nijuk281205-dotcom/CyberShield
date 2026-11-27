import json
import os
import sqlite3
from contextlib import contextmanager

SCHEMA = """
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL CHECK (kind IN ('url', 'text')),
    input TEXT NOT NULL,
    risk_level TEXT NOT NULL CHECK (risk_level IN ('Low', 'Medium', 'High')),
    score INTEGER NOT NULL,
    summary TEXT NOT NULL,
    findings TEXT NOT NULL,
    recommendations TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_scans_created ON scans (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scans_risk ON scans (risk_level);
"""


def init_db(path):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with connect(path) as conn:
        conn.executescript(SCHEMA)


@contextmanager
def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _row(r):
    return {
        "id": r["id"],
        "kind": r["kind"],
        "input": r["input"],
        "risk_level": r["risk_level"],
        "score": r["score"],
        "summary": r["summary"],
        "findings": json.loads(r["findings"]),
        "recommendations": json.loads(r["recommendations"]),
        "created_at": r["created_at"],
    }


def save_scan(path, kind, text, result):
    with connect(path) as conn:
        cur = conn.execute(
            "INSERT INTO scans (kind, input, risk_level, score, summary, findings, recommendations) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (kind, text, result["risk_level"], result["score"], result["summary"],
             json.dumps(result["findings"]), json.dumps(result["recommendations"])),
        )
        row = conn.execute("SELECT * FROM scans WHERE id = ?", (cur.lastrowid,)).fetchone()
        return _row(row)


def list_scans(path, search="", risk="", kind="", page=1, per_page=10):
    where, params = [], []
    if search:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        where.append("input LIKE ? ESCAPE '\\'")
        params.append(f"%{escaped}%")
    if risk:
        where.append("risk_level = ?")
        params.append(risk)
    if kind:
        where.append("kind = ?")
        params.append(kind)
    clause = ("WHERE " + " AND ".join(where)) if where else ""
    with connect(path) as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM scans {clause}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM scans {clause} ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
            params + [per_page, (page - 1) * per_page],
        ).fetchall()
    return [_row(r) for r in rows], total


def delete_scan(path, scan_id):
    with connect(path) as conn:
        return conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,)).rowcount > 0


def clear_scans(path):
    with connect(path) as conn:
        return conn.execute("DELETE FROM scans").rowcount


def get_stats(path):
    with connect(path) as conn:
        total = conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
        by_risk = {"Low": 0, "Medium": 0, "High": 0}
        for r in conn.execute("SELECT risk_level, COUNT(*) c FROM scans GROUP BY risk_level"):
            by_risk[r["risk_level"]] = r["c"]
        by_kind = {"url": 0, "text": 0}
        for r in conn.execute("SELECT kind, COUNT(*) c FROM scans GROUP BY kind"):
            by_kind[r["kind"]] = r["c"]
        daily = [
            {"date": r["d"], "count": r["c"]}
            for r in conn.execute(
                "SELECT substr(created_at, 1, 10) d, COUNT(*) c FROM scans "
                "WHERE created_at >= date('now', '-6 days') GROUP BY d ORDER BY d"
            )
        ]
        recent = [_row(r) for r in conn.execute("SELECT * FROM scans ORDER BY created_at DESC, id DESC LIMIT 5")]
    return {"total": total, "by_risk": by_risk, "by_kind": by_kind, "daily": daily, "recent": recent}
