#!/usr/bin/env python3
"""
main.py — CLI entry point for the Braj spelling correction agent.

Modes:
  (default)     Run the correction pipeline interactively
  --resume      Resume a previous run from checkpoint
  --redo-batch  Re-run a specific batch
  --status      Show batch progress table
  --build       Build output DOCX from accepted corrections (no agents)
"""

import argparse
import json
import sys
from pathlib import Path

# Load .env from the agent directory before anything else
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

# Add agent dir to path so local modules resolve
sys.path.insert(0, str(Path(__file__).parent))

from db import get_status_table, init_db, reset_batch_to_pending
from docx_utils import build_output_docx
from graph import build_graph
from langgraph.types import Command


DEFAULT_MODEL = "gemini-2.0-flash"
DEFAULT_BATCH_SIZE = 30


# ---------------------------------------------------------------------------
# Interactive review loop
# ---------------------------------------------------------------------------

def run_review_loop(graph, checkpointer, initial_state: dict, thread_id: str) -> None:
    """
    Drive the graph forward, pausing at each interrupt for human input.
    """
    config = {"configurable": {"thread_id": thread_id}}

    # Check if this thread already has state (resume)
    existing = checkpointer.get(config)
    if existing:
        print(f"Resuming from checkpoint (thread: {thread_id})\n")
        events = graph.stream(None, config=config, stream_mode="values")
    else:
        events = graph.stream(initial_state, config=config, stream_mode="values")

    while True:
        try:
            for event in events:
                pass  # consume until interrupt or end
            print("\nAll batches processed.")
            break

        except Exception as exc:
            # LangGraph raises when graph is interrupted
            state = graph.get_state(config)
            if not state.next:
                break

            # Find interrupt payload
            interrupts = [
                task.interrupts for task in state.tasks if task.interrupts
            ]
            if not interrupts:
                raise

            payload = interrupts[0][0].value
            print(payload["display"])

            decision = prompt_user(payload["corrections"], payload["batch_id"])

            if decision["action"] == "quit":
                print("\nProgress saved. Resume with: --resume")
                sys.exit(0)

            # Resume graph with human decision
            events = graph.stream(
                Command(resume=decision),
                config=config,
                stream_mode="values",
            )


def prompt_user(corrections: list, batch_id: int) -> dict:
    """Handle terminal input for a batch review."""
    while True:
        try:
            raw = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            return {"action": "quit", "edits": {}}

        if raw == "" or raw.lower() == "y":
            return {"action": "accept", "edits": {}}

        if raw.lower() == "s":
            return {"action": "skip", "edits": {}}

        if raw.lower() == "r":
            return {"action": "rerun", "edits": {}}

        if raw.lower() == "q":
            return {"action": "quit", "edits": {}}

        if raw.lower().startswith("e "):
            # Edit a specific paragraph: e <idx> <new text>
            parts = raw[2:].split(" ", 1)
            if len(parts) == 2:
                try:
                    idx = int(parts[0])
                    new_text = parts[1]
                    edits = {str(c["index"]): c["corrected"] for c in corrections}
                    edits[str(idx)] = new_text
                    print(f"  Edited [{idx}] → {new_text}")
                    print("  Press [Enter] to accept with this edit, or keep editing.")
                    continue
                except ValueError:
                    pass

        print("  Commands: [Enter]=Accept  [s]=Skip  [r]=Re-run  [e <idx> <text>]=Edit  [q]=Quit")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(
        description="Braj Devanagari spelling correction agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    p.add_argument("--input",  "-i", help="Source DOCX path")
    p.add_argument("--output", "-o", help="Output DOCX path (used with --build)")
    p.add_argument("--checkpoint", "-c", default="progress/run_001.db",
                   help="SQLite checkpoint DB path (default: progress/run_001.db)")
    p.add_argument("--api-key", "-k", help="Google Gemini API key")
    p.add_argument("--model", "-m", default=DEFAULT_MODEL,
                   help=f"Gemini model (default: {DEFAULT_MODEL})")
    p.add_argument("--batch-size", "-b", type=int, default=DEFAULT_BATCH_SIZE,
                   help=f"Paragraphs per batch (default: {DEFAULT_BATCH_SIZE})")
    p.add_argument("--thread-id", default="braj-run-001",
                   help="LangGraph thread ID (change to start a fresh run on the same DB)")

    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--resume", action="store_true",
                      help="Resume the most recent run from checkpoint")
    mode.add_argument("--redo-batch", type=int, metavar="BATCH_ID",
                      help="Reset a batch to pending and re-run it")
    mode.add_argument("--status", action="store_true",
                      help="Show batch progress table and exit")
    mode.add_argument("--build", action="store_true",
                      help="Build output DOCX from accepted corrections (no agents)")

    return p.parse_args()


def log_path_from_db(db_path: str) -> str:
    return str(Path(db_path).with_suffix(".jsonl"))


def main():
    args = parse_args()
    db_path = args.checkpoint
    log_path = log_path_from_db(db_path)

    # ── --status ────────────────────────────────────────────────────────────
    if args.status:
        if not Path(db_path).exists():
            print(f"No checkpoint DB found at: {db_path}")
            sys.exit(1)
        print(get_status_table(db_path))
        return

    # ── --build ─────────────────────────────────────────────────────────────
    if args.build:
        if not args.input or not args.output:
            print("--build requires --input and --output")
            sys.exit(1)
        applied = build_output_docx(args.input, log_path, args.output)
        print(f"Built {args.output} with {applied} correction(s) applied.")
        return

    # ── --redo-batch ─────────────────────────────────────────────────────────
    if args.redo_batch is not None:
        if not Path(db_path).exists():
            print(f"No checkpoint DB found at: {db_path}")
            sys.exit(1)
        reset_batch_to_pending(db_path, args.redo_batch)
        # Remove that batch's entries from the log
        log_file = Path(log_path)
        if log_file.exists():
            lines = log_file.read_text(encoding="utf-8").splitlines()
            kept = [l for l in lines if json.loads(l).get("batch_id") != args.redo_batch]
            log_file.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
        print(f"Batch {args.redo_batch} reset to pending. Resuming from checkpoint...")
        args.resume = True

    # ── run / resume ─────────────────────────────────────────────────────────
    if not args.resume and not args.input:
        print("Provide --input to start a new run, or --resume to continue.")
        sys.exit(1)

    if not args.api_key:
        import os
        args.api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not args.api_key:
            print("Provide --api-key or set GOOGLE_API_KEY / GEMINI_API_KEY env var.")
            sys.exit(1)

    init_db(db_path)
    graph, checkpointer = build_graph(db_path)

    initial_state = {
        "input_path":   args.input or "",
        "checkpoint_db": db_path,
        "log_path":     log_path,
        "api_key":      args.api_key,
        "model":        args.model,
        "batch_size":   args.batch_size,
        "paragraphs":   [],
        "total_batches": 0,
        "current_batch_id": 0,
        "current_entries":  [],
        "pending_corrections": [],
        "human_decision": {},
        "errors": [],
    }

    run_review_loop(graph, checkpointer, initial_state, args.thread_id)


if __name__ == "__main__":
    main()
