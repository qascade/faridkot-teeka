# Braj Correction Agent

A LangGraph + Gemini pipeline for incrementally correcting Devanagari spelling errors in the Fareedkot Teeka Devanagari DOCX. Designed for human-in-the-loop review with full resumability.

---

## What it does

The Devanagari DOCX (`fareedkot_teeka_devanagari_0_1_0.docx`) was produced by machine-transliterating Gurmukhi to Devanagari character-by-character. This introduces mechanical spelling errors — wrong matra ordering, anusvara/chandrabindu confusion, stray virama artifacts, and nukta issues.

This agent:
1. Extracts all Braj commentary paragraphs (identified by color — maroon and blue)
2. Sends them in batches to Gemini for spelling correction
3. Pauses after each batch for you to review, edit, or skip proposed changes
4. Saves progress to a SQLite checkpoint so you can quit and resume at any time
5. Builds the corrected DOCX on demand from the accepted corrections log

**Scope:** Spelling fixes only. Vocabulary and Braj Bhasha forms are not changed in this phase.

---

## Setup

### 1. Install dependencies

```bash
# From the project root
pip install -r braj_correction_agent/requirements.txt
```

### 2. Add your Gemini API key

Edit `braj_correction_agent/.env`:

```
GOOGLE_API_KEY=your_key_here
```

The `.env` file is gitignored and loaded automatically on startup.

---

## Usage

### Start a new correction run

```bash
python braj_correction_agent/main.py \
  --input "Finished Docs/fareedkot_teeka_devanagari_0_1_0.docx"
```

### Resume after quitting

```bash
python braj_correction_agent/main.py --resume
```

### Check progress

```bash
python braj_correction_agent/main.py --status
```

Example output:
```
Progress: 47/215 batches  [████████░░░░░░░░░░░░]  22%
Total corrections accepted: 134

 Batch  Paragraphs      Status        Changes  Timestamp
────────────────────────────────────────────────────────
     0  0-29            accepted           3   2026-04-03T10:23
     1  30-59           accepted           7   2026-04-03T10:24
     2  60-89           skipped            0   2026-04-03T10:25
    ...
    47  1410-1439       accepted           2   2026-04-03T10:58
    48  1440-1469       in_progress
    49+                 pending
```

### Re-run a specific batch

```bash
python braj_correction_agent/main.py --redo-batch 2 --resume
```

Resets batch 2 to pending, removes its prior corrections from the log, and re-runs it through Gemini for a fresh review.

### Build the corrected DOCX

Run this any time to produce the output document from all currently accepted corrections. The source DOCX is never modified.

```bash
python braj_correction_agent/main.py --build \
  --input  "Finished Docs/fareedkot_teeka_devanagari_0_1_0.docx" \
  --output "Finished Docs/fareedkot_teeka_devanagari_0_2_0.docx"

# Output is fareedkot_teeka_devanagari_0_2_0.docx (v0.2.0)
```

---

## Review prompt

After each batch Gemini proposes corrections:

```
─── Batch 48/215 ── 30 paragraphs ───────────────────────────────
  [1440]  हुइ  →  हुई
  [1447]  जाइयो  →  जाइए
  [1453]  बंूद  →  बूंद

  [Enter]=Accept all   [s]=Skip   [r]=Re-run   [e <idx> <text>]=Edit   [q]=Quit & save
> 
```

| Command | Action |
|---------|--------|
| `Enter` | Accept all proposed corrections for this batch |
| `s` | Skip this batch (keep original text, mark as skipped) |
| `r` | Re-send this batch to Gemini for a fresh attempt |
| `e 1447 जाएं` | Override the correction for paragraph 1447 with your own text |
| `q` | Save progress and quit — resume anytime with `--resume` |

---

## Progress files

```
progress/
  run_001.db      — LangGraph checkpoint + batch status table (SQLite)
  run_001.jsonl   — append-only log of every accepted correction
```

The `.jsonl` log is human-readable and editable. Each line:
```json
{"batch_id": 4, "para_idx": 1447, "original": "जाइयो", "corrected": "जाइए", "status": "accepted", "timestamp": "..."}
```

To rebuild the DOCX after manually editing the log, just re-run `--build`.

---

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | — | Source DOCX path (required for new runs) |
| `--output` | — | Output DOCX path (required for `--build`) |
| `--checkpoint` | `progress/run_001.db` | SQLite DB path |
| `--api-key` | from `.env` | Gemini API key |
| `--model` | `gemini-2.0-flash` | Gemini model |
| `--batch-size` | `30` | Paragraphs per batch |
| `--thread-id` | `braj-run-001` | LangGraph thread ID (change to start a parallel run) |

---

## File structure

```
braj_correction_agent/
├── main.py          — CLI entry point (all modes)
├── graph.py         — LangGraph pipeline + SqliteSaver checkpointing
├── nodes.py         — extract, batch, process, review, record nodes
├── docx_utils.py    — DOCX paragraph extraction and output building
├── db.py            — SQLite batch tracking helpers
├── prompts.py       — Gemini prompt template
├── requirements.txt — Python dependencies
└── .env             — API key (gitignored)
```

---

## Paragraph type detection

Paragraphs are identified by the color of their first run, as set by `src/generate.py`:

| Color | Type | Action |
|-------|------|--------|
| `800000` (maroon) | Braj commentary | Corrected |
| `0000FF` (blue) | Braj sub-commentary | Corrected |
| `00007F` (navy) | Gurbani scripture | **Never touched** |
| `C0006A` (purple) | GGS references | Skipped |
| `555555` (gray) | Annotations | Skipped |
