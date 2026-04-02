"""
nodes.py — LangGraph node functions for the braj correction pipeline.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from langgraph.types import interrupt

from db import (
    get_next_pending_batch,
    insert_batches,
    upsert_batch,
)
from docx_utils import extract_braj_paragraphs
from prompts import SPELLING_CORRECTION_PROMPT


# ---------------------------------------------------------------------------
# extract_node
# ---------------------------------------------------------------------------

def extract_node(state: dict) -> dict:
    """Read the source DOCX and extract all Braj paragraphs."""
    print(f"Extracting Braj paragraphs from: {state['input_path']}")
    paragraphs = extract_braj_paragraphs(state["input_path"])
    print(f"  Found {len(paragraphs)} Braj/Braj_sub paragraphs.")

    # Divide into batches and register them in the DB
    batch_size = state["batch_size"]
    batch_ranges = []
    for i in range(0, len(paragraphs), batch_size):
        batch_id = i // batch_size
        chunk = paragraphs[i : i + batch_size]
        para_start = chunk[0]["para_idx"]
        para_end = chunk[-1]["para_idx"]
        batch_ranges.append((batch_id, para_start, para_end))

    insert_batches(state["checkpoint_db"], batch_ranges)
    total_batches = len(batch_ranges)
    print(f"  Created {total_batches} batches of up to {batch_size} paragraphs.\n")

    return {"paragraphs": paragraphs, "total_batches": total_batches}


# ---------------------------------------------------------------------------
# batch_node  — advance to next pending batch
# ---------------------------------------------------------------------------

def batch_node(state: dict) -> dict:
    """Find the next pending batch and slice the relevant paragraphs."""
    batch_info = get_next_pending_batch(state["checkpoint_db"])
    if batch_info is None:
        return {"current_batch_id": -1, "current_entries": []}

    batch_id = batch_info["batch_id"]
    upsert_batch(state["checkpoint_db"], batch_id, "in_progress")

    # Slice paragraphs belonging to this batch
    batch_size = state["batch_size"]
    start = batch_id * batch_size
    end = start + batch_size
    entries = state["paragraphs"][start:end]

    return {"current_batch_id": batch_id, "current_entries": entries}


# ---------------------------------------------------------------------------
# process_node  — call Gemini
# ---------------------------------------------------------------------------

def process_node(state: dict) -> dict:
    """Send current batch to Gemini and collect proposed corrections."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage

    entries = state["current_entries"]
    if not entries:
        return {"pending_corrections": []}

    numbered = "\n".join(
        f'{e["para_idx"]}: {e["text"]}' for e in entries
    )
    prompt = SPELLING_CORRECTION_PROMPT.format(numbered_paragraphs=numbered)

    llm = ChatGoogleGenerativeAI(
        model=state.get("model", "gemini-2.0-flash"),
        google_api_key=state["api_key"],
        temperature=0,
    )

    errors = list(state.get("errors", []))
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        corrections = json.loads(raw)
        if not isinstance(corrections, list):
            raise ValueError("Response is not a JSON array")

        # Validate: only keep entries with known para_idx values
        valid_indices = {e["para_idx"] for e in entries}
        corrections = [
            c for c in corrections
            if isinstance(c, dict)
            and "index" in c
            and "corrected" in c
            and c["index"] in valid_indices
        ]
        return {"pending_corrections": corrections, "errors": errors}

    except Exception as exc:
        batch_id = state["current_batch_id"]
        errors.append(f"Batch {batch_id}: {exc}")
        upsert_batch(state["checkpoint_db"], batch_id, "skipped")
        return {"pending_corrections": [], "errors": errors}


# ---------------------------------------------------------------------------
# review_node  — human-in-the-loop interrupt
# ---------------------------------------------------------------------------

def review_node(state: dict) -> dict:
    """
    Interrupt the graph and present proposed corrections for human review.

    The interrupt payload is shown to the user. They resume the graph by
    calling graph.invoke(Command(resume=decision)) where decision is a dict
    with keys: action ('accept'|'skip'|'rerun'), edits (dict para_idx->text).
    """
    corrections = state["pending_corrections"]
    batch_id = state["current_batch_id"]
    total = state.get("total_batches", "?")
    entries = state["current_entries"]

    # Build display lines
    lines = [f"\n─── Batch {batch_id + 1}/{total} ── {len(entries)} paragraphs ───────────────────"]
    if not corrections:
        lines.append("  (no spelling corrections proposed for this batch)")
    else:
        for c in corrections:
            orig = next((e["text"] for e in entries if e["para_idx"] == c["index"]), "?")
            lines.append(f'  [{c["index"]}]  {orig}')
            lines.append(f'        →  {c["corrected"]}')
    lines.append("")
    lines.append("  [Enter] Accept all   [e <idx>] Edit   [s] Skip   [r] Re-run   [q] Quit & save")

    decision = interrupt({"display": "\n".join(lines), "corrections": corrections, "batch_id": batch_id})
    return {"human_decision": decision}


# ---------------------------------------------------------------------------
# record_node  — persist accepted corrections
# ---------------------------------------------------------------------------

def record_node(state: dict) -> dict:
    """Apply human decision: write to log, update DB status."""
    decision = state.get("human_decision", {})
    action = decision.get("action", "accept")
    edits: dict = decision.get("edits", {})
    batch_id = state["current_batch_id"]
    log_path = state["log_path"]

    if action == "skip":
        upsert_batch(state["checkpoint_db"], batch_id, "skipped")
        return {}

    if action == "rerun":
        from db import reset_batch_to_pending
        reset_batch_to_pending(state["checkpoint_db"], batch_id)
        return {}

    # Accept (possibly with edits)
    corrections = list(state.get("pending_corrections", []))
    for c in corrections:
        if str(c["index"]) in edits:
            c["corrected"] = edits[str(c["index"])]

    ts = datetime.now(timezone.utc).isoformat()
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a", encoding="utf-8") as f:
        for c in corrections:
            entry = {
                "batch_id": batch_id,
                "para_idx": c["index"],
                "original": next(
                    (e["text"] for e in state["current_entries"] if e["para_idx"] == c["index"]),
                    "",
                ),
                "corrected": c["corrected"],
                "status": "accepted",
                "timestamp": ts,
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    upsert_batch(state["checkpoint_db"], batch_id, "accepted", changes=len(corrections))
    print(f"  ✓ Batch {batch_id + 1}: {len(corrections)} correction(s) recorded.")
    return {}


# ---------------------------------------------------------------------------
# Router: should_continue
# ---------------------------------------------------------------------------

def should_continue(state: dict) -> str:
    """Route: if no more pending batches, end; otherwise loop."""
    if state.get("current_batch_id", -1) == -1:
        return "end"
    action = state.get("human_decision", {}).get("action", "accept")
    if action == "quit":
        return "end"
    return "continue"
