"""
db.py — SQLite helpers for batch tracking.

The same DB file is used for both LangGraph checkpointing and the batches table.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def init_db(db_path: str) -> None:
    """Create the batches table if it doesn't exist."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS batches (
                batch_id    INTEGER PRIMARY KEY,
                para_start  INTEGER NOT NULL,
                para_end    INTEGER NOT NULL,
                status      TEXT NOT NULL DEFAULT 'pending',
                changes     INTEGER DEFAULT 0,
                timestamp   TEXT
            )
        """)
        conn.commit()


def insert_batches(db_path: str, batch_ranges: list[tuple[int, int, int]]) -> None:
    """
    Insert batch records with status=pending.
    batch_ranges: list of (batch_id, para_start, para_end)
    Skips batches that already exist.
    """
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            """INSERT OR IGNORE INTO batches (batch_id, para_start, para_end, status)
               VALUES (?, ?, ?, 'pending')""",
            batch_ranges,
        )
        conn.commit()


def upsert_batch(db_path: str, batch_id: int, status: str, changes: int = 0) -> None:
    """Update a batch's status and change count."""
    ts = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """UPDATE batches SET status=?, changes=?, timestamp=?
               WHERE batch_id=?""",
            (status, changes, ts, batch_id),
        )
        conn.commit()


def get_next_pending_batch(db_path: str) -> dict | None:
    """Return the lowest-id pending batch, or None if all done."""
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT batch_id, para_start, para_end FROM batches WHERE status='pending' ORDER BY batch_id LIMIT 1"
        ).fetchone()
    if row is None:
        return None
    return {"batch_id": row[0], "para_start": row[1], "para_end": row[2]}


def reset_batch_to_pending(db_path: str, batch_id: int) -> None:
    """Reset a batch to pending (used by --redo-batch)."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "UPDATE batches SET status='pending', changes=0, timestamp=NULL WHERE batch_id=?",
            (batch_id,),
        )
        conn.commit()


def get_status_table(db_path: str) -> str:
    """Return a formatted status summary string."""
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT batch_id, para_start, para_end, status, changes, timestamp FROM batches ORDER BY batch_id"
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0]
        done = conn.execute(
            "SELECT COUNT(*) FROM batches WHERE status IN ('accepted','skipped','redone')"
        ).fetchone()[0]
        total_changes = conn.execute(
            "SELECT SUM(changes) FROM batches WHERE status='accepted'"
        ).fetchone()[0] or 0

    if not rows:
        return "No batches found. Run with --input to start a new session."

    pct = int(done / total * 100) if total else 0
    bar_filled = int(pct / 5)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)

    lines = [
        f"\nProgress: {done}/{total} batches  [{bar}]  {pct}%",
        f"Total corrections accepted: {total_changes}\n",
        f"{'Batch':>6}  {'Paragraphs':<14}  {'Status':<12}  {'Changes':>7}  Timestamp",
        "─" * 68,
    ]
    for batch_id, para_start, para_end, status, changes, ts in rows:
        ts_short = ts[:16] if ts else "—"
        changes_str = str(changes) if changes else "—"
        lines.append(
            f"{batch_id:>6}  {para_start}-{para_end:<10}  {status:<12}  {changes_str:>7}  {ts_short}"
        )
    return "\n".join(lines)
