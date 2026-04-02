"""
graph.py — LangGraph graph definition for the braj correction pipeline.
"""

from typing import Annotated
import operator

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from nodes import (
    extract_node,
    batch_node,
    process_node,
    review_node,
    record_node,
    should_continue,
)


# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------

class GraphState(dict):
    """
    Typed keys used in state (plain dict subclass for LangGraph compatibility).

    input_path:          str   — source DOCX path
    checkpoint_db:       str   — SQLite DB path (checkpoints + batch tracking)
    log_path:            str   — corrections_log.jsonl path
    api_key:             str   — Gemini API key
    model:               str   — Gemini model name
    batch_size:          int   — paragraphs per batch
    paragraphs:          list  — all extracted Braj paragraphs
    total_batches:       int
    current_batch_id:    int   — -1 means no more batches
    current_entries:     list  — paragraphs in current batch
    pending_corrections: list  — Gemini-proposed corrections
    human_decision:      dict  — result of human review interrupt
    errors:              list  — accumulated error messages
    """


def build_graph(db_path: str) -> tuple:
    """
    Build and compile the LangGraph correction pipeline.

    Returns (compiled_graph, checkpointer).
    """
    checkpointer = SqliteSaver.from_conn_string(db_path)

    builder = StateGraph(dict)

    builder.add_node("extract",  extract_node)
    builder.add_node("batch",    batch_node)
    builder.add_node("process",  process_node)
    builder.add_node("review",   review_node)
    builder.add_node("record",   record_node)

    builder.set_entry_point("extract")
    builder.add_edge("extract", "batch")
    builder.add_edge("batch",   "process")
    builder.add_edge("process", "review")
    builder.add_edge("review",  "record")

    builder.add_conditional_edges(
        "record",
        should_continue,
        {"continue": "batch", "end": END},
    )

    graph = builder.compile(checkpointer=checkpointer)
    return graph, checkpointer
