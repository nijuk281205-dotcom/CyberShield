from flask import Blueprint, current_app, jsonify, request

from database import db
from services import analyzer

api = Blueprint("api", __name__, url_prefix="/api")


def _path():
    return current_app.config["DATABASE_PATH"]


def _error(message, status=400):
    return jsonify({"error": message}), status


@api.get("/health")
def health():
    return jsonify({"status": "ok"})


@api.post("/scan")
def scan():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error('Send a JSON body like {"type": "url", "input": "..."}.')
    kind = data.get("type")
    value = data.get("input")
    if kind not in ("url", "text"):
        return _error("'type' must be 'url' or 'text'.")
    if not isinstance(value, str) or not value.strip():
        return _error("'input' is required.")
    value = "".join(ch for ch in value.strip() if ch == "\n" or ch >= " ")

    cfg = current_app.config
    if kind == "url":
        if len(value) > cfg["MAX_URL_LENGTH"]:
            return _error(f"URL is too long (max {cfg['MAX_URL_LENGTH']} characters).")
        if any(c.isspace() for c in value):
            return _error("A URL cannot contain spaces. Use Message mode to check text.")
        result = analyzer.analyze_url(value)
        if result is None:
            return _error("That doesn't look like a valid URL.")
    else:
        if len(value) > cfg["MAX_TEXT_LENGTH"]:
            return _error(f"Message is too long (max {cfg['MAX_TEXT_LENGTH']} characters).")
        result = analyzer.analyze_text(value)

    saved = db.save_scan(_path(), kind, value, result)
    saved["limitations"] = result["limitations"]
    return jsonify(saved), 201


@api.get("/history")
def history():
    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = min(max(int(request.args.get("per_page", 10)), 1), 100)
    except ValueError:
        return _error("'page' and 'per_page' must be numbers.")
    risk = request.args.get("risk", "")
    kind = request.args.get("type", "")
    if risk not in ("", "Low", "Medium", "High"):
        return _error("'risk' must be Low, Medium or High.")
    if kind not in ("", "url", "text"):
        return _error("'type' must be url or text.")
    search = request.args.get("search", "")[:200]
    items, total = db.list_scans(_path(), search, risk, kind, page, per_page)
    return jsonify({"items": items, "total": total, "page": page, "per_page": per_page,
                    "pages": max((total + per_page - 1) // per_page, 1)})


@api.delete("/history/<int:scan_id>")
def delete_one(scan_id):
    if not db.delete_scan(_path(), scan_id):
        return _error("Record not found.", 404)
    return jsonify({"deleted": scan_id})


@api.delete("/history")
def delete_all():
    return jsonify({"deleted": db.clear_scans(_path())})


@api.get("/stats")
def stats():
    return jsonify(db.get_stats(_path()))
