"""
test_gurbani_accuracy.py — Compare Gurbani lines in a generated docx against
the authoritative Unicode GGS reference downloaded from GurbaniDB.

Uses sequential ordered matching with LCS-style alignment so that repeated
lines (like rahao) are each verified independently.
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone
from difflib import SequenceMatcher

from docx import Document
from docx.shared import RGBColor

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REF = os.path.join(SCRIPT_DIR, "data", "ggs_reference.json")
DEFAULT_OUTPUT = os.path.join(SCRIPT_DIR, "data", "gurbani_discrepancies.json")

GURBANI_COLOR = RGBColor(0x00, 0x00, 0x7F)
GGS_REF_COLOR = RGBColor(0xC0, 0x00, 0x6A)
PAGE_MARKER_RE = re.compile(r"^─── Page (\d+) ───$")

# Gurmukhi digits → ASCII digits
_GURMUKHI_DIGITS = str.maketrans("੦੧੨੩੪੫੬੭੮੯", "0123456789")

# Section ranges for per-section accuracy
SECTION_SIZE = 100

# Confidence thresholds
HIGH_CONFIDENCE = 0.95
DEFAULT_LOW_THRESHOLD = 0.85


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_ggs_page(text: str) -> int | None:
    """Extract GGS page number from a ggs_ref paragraph like 'ਪੰਨਾ ੧੨੩'."""
    text = text.strip()
    if not text.startswith("ਪੰਨਾ"):
        return None
    num_str = text.replace("ਪੰਨਾ", "").strip().translate(_GURMUKHI_DIGITS)
    try:
        return int(num_str)
    except ValueError:
        return None


def split_into_tuks(text: str) -> list[str]:
    """Split a gurbani paragraph into individual tuks by dandas.

    Re-merges trailing pauri numbers (e.g. ॥੧੦॥) back onto the previous tuk,
    since the GGS reference keeps them as part of the line.
    """
    parts = re.split(r"(?<=[।॥])", text)
    parts = [p.strip() for p in parts if p.strip()]

    # Re-merge: if a part is just digits + dandas, append it to the previous part
    merged = []
    for part in parts:
        stripped = part.replace("॥", "").replace("।", "").replace(" ", "")
        is_number = stripped and all(c in "੦੧੨੩੪੫੬੭੮੯0123456789" for c in stripped)
        if is_number and merged:
            merged[-1] = merged[-1] + " " + part
        else:
            merged.append(part)
    return merged


def is_structural_marker(tuk: str) -> bool:
    """Check if a tuk is a structural marker (pauri number, standalone rahao, etc.)."""
    stripped = tuk.replace("॥", "").replace("।", "").replace(" ", "")
    # Pauri/stanza numbers: ੧, ੨੩, etc.
    if stripped and all(c in "੦੧੨੩੪੫੬੭੮੯0123456789" for c in stripped):
        return True
    # Standalone rahao
    if stripped in ("ਰਹਾਉ", "ਰਹਾਉਦੂਜਾ"):
        return True
    return False


def normalize_for_compare(text: str) -> str:
    """Normalize text for fuzzy comparison."""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("।", "").replace("॥", "")
    text = " ".join(text.split())
    return text.strip()


def similarity(a: str, b: str) -> float:
    """Compute similarity ratio between two normalized strings."""
    na = normalize_for_compare(a)
    nb = normalize_for_compare(b)
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def confidence_label(sim: float, threshold: float) -> str:
    """Assign confidence band label."""
    if sim >= HIGH_CONFIDENCE:
        return "high"
    elif sim >= threshold:
        return "low"
    else:
        return "mismatch"


# ---------------------------------------------------------------------------
# Docx extraction
# ---------------------------------------------------------------------------

def extract_gurbani_from_docx(docx_path: str) -> list[dict]:
    """
    Extract gurbani tuks from docx, grouped by GGS page.

    Returns a list of dicts: {pdf_page, ggs_page, tuk}
    """
    doc = Document(docx_path)
    results = []
    current_pdf_page = None
    current_ggs_page = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Detect page marker
        m = PAGE_MARKER_RE.match(text)
        if m:
            current_pdf_page = int(m.group(1))
            continue

        if not para.runs:
            continue
        run = para.runs[0]

        try:
            color = run.font.color.rgb
        except (TypeError, AttributeError):
            continue

        # Detect ggs_ref paragraph
        if color == GGS_REF_COLOR:
            page_num = parse_ggs_page(text)
            if page_num is not None:
                current_ggs_page = page_num
            continue

        # Detect gurbani paragraph
        if color == GURBANI_COLOR and run.font.bold:
            tuks = split_into_tuks(text)
            for tuk in tuks:
                if is_structural_marker(tuk):
                    continue  # Skip pauri numbers, standalone rahao, etc.
                results.append({
                    "pdf_page": current_pdf_page,
                    "ggs_page": current_ggs_page,
                    "tuk": tuk,
                })

    return results


# ---------------------------------------------------------------------------
# Sequential ordered matching with LCS-style alignment
# ---------------------------------------------------------------------------

def match_tuks_for_page(
    docx_tuks: list[str],
    ref_lines: list[str],
    threshold: float,
) -> list[dict]:
    """
    Match docx tuks against reference lines using ordered sequential matching.

    Walks both lists in order. When a docx tuk matches a reference line above
    threshold, both are consumed. This ensures repeated lines (like rahao)
    are each matched independently.

    Returns a list of match results for each docx tuk.
    """
    results = []
    ref_used = [False] * len(ref_lines)

    # Normalize reference lines once
    ref_normalized = [normalize_for_compare(line) for line in ref_lines]

    # For each docx tuk, find the best unused reference line in order
    ref_start = 0  # Track where to start searching (maintains ordering)

    for tuk in docx_tuks:
        tuk_norm = normalize_for_compare(tuk)
        if not tuk_norm:
            results.append({
                "tuk": tuk,
                "best_match": "",
                "similarity": 0.0,
                "confidence": "skipped",
            })
            continue

        best_sim = 0.0
        best_idx = -1

        # Search from ref_start forward (ordered matching)
        for j in range(ref_start, len(ref_lines)):
            if ref_used[j]:
                continue
            sim = SequenceMatcher(None, tuk_norm, ref_normalized[j]).ratio()
            if sim > best_sim:
                best_sim = sim
                best_idx = j
                if sim >= HIGH_CONFIDENCE:
                    break  # Good enough, no need to search further

        # Also check backwards a few lines for flexibility (handles minor reordering)
        for j in range(max(0, ref_start - 3), ref_start):
            if ref_used[j]:
                continue
            sim = SequenceMatcher(None, tuk_norm, ref_normalized[j]).ratio()
            if sim > best_sim:
                best_sim = sim
                best_idx = j

        if best_idx >= 0 and best_sim >= threshold:
            ref_used[best_idx] = True
            ref_start = best_idx + 1
            results.append({
                "tuk": tuk,
                "best_match": ref_lines[best_idx],
                "similarity": round(best_sim, 4),
                "confidence": confidence_label(best_sim, threshold),
            })
        else:
            results.append({
                "tuk": tuk,
                "best_match": ref_lines[best_idx] if best_idx >= 0 else "",
                "similarity": round(best_sim, 4),
                "confidence": "mismatch",
            })

    return results


# ---------------------------------------------------------------------------
# Main test logic
# ---------------------------------------------------------------------------

def run_accuracy_test(
    docx_path: str,
    ref_path: str = DEFAULT_REF,
    output_path: str = DEFAULT_OUTPUT,
    threshold: float = DEFAULT_LOW_THRESHOLD,
) -> dict:
    # Load reference
    if not os.path.exists(ref_path):
        print(f"ERROR: Reference not found at {ref_path}", file=sys.stderr)
        print("Run download_ggs_reference.py first.", file=sys.stderr)
        sys.exit(1)

    with open(ref_path, "r", encoding="utf-8") as f:
        reference = json.load(f)

    print(f"Loaded reference: {len(reference)} pages")

    # Extract gurbani from docx
    print(f"Extracting gurbani from {docx_path}...")
    all_tuks = extract_gurbani_from_docx(docx_path)
    print(f"Found {len(all_tuks)} tuks")

    # Group tuks by GGS page
    tuks_by_page: dict[int, list[dict]] = {}
    skipped_no_page = 0
    for entry in all_tuks:
        if entry["ggs_page"] is None:
            skipped_no_page += 1
            continue
        tuks_by_page.setdefault(entry["ggs_page"], []).append(entry)

    if skipped_no_page:
        print(f"  Skipped {skipped_no_page} tuks with no GGS page reference")

    # Match tuks against reference page by page
    all_results = []
    discrepancies = []
    section_stats: dict[str, dict] = {}

    for ggs_page, page_tuks in sorted(tuks_by_page.items()):
        # Collect reference lines: current page + adjacent pages
        ref_lines = []
        for p in [ggs_page - 1, ggs_page, ggs_page + 1]:
            if str(p) in reference:
                ref_lines.extend(reference[str(p)])

        docx_tuk_texts = [t["tuk"] for t in page_tuks]
        matches = match_tuks_for_page(docx_tuk_texts, ref_lines, threshold)

        for entry, match in zip(page_tuks, matches):
            result = {
                "pdf_page": entry["pdf_page"],
                "ggs_page": entry["ggs_page"],
                **match,
            }
            all_results.append(result)

            if match["confidence"] in ("low", "mismatch"):
                discrepancies.append(result)

            # Track per-section stats
            section_start = ((ggs_page - 1) // SECTION_SIZE) * SECTION_SIZE + 1
            section_end = min(section_start + SECTION_SIZE - 1, 1430)
            section_key = f"{section_start}-{section_end}"
            if section_key not in section_stats:
                section_stats[section_key] = {"tested": 0, "high": 0, "low": 0, "mismatch": 0, "skipped": 0}
            section_stats[section_key]["tested"] += 1
            section_stats[section_key][match["confidence"]] += 1

    # Compute stats
    total = len(all_results)
    high = sum(1 for r in all_results if r["confidence"] == "high")
    low = sum(1 for r in all_results if r["confidence"] == "low")
    mismatch = sum(1 for r in all_results if r["confidence"] == "mismatch")
    skipped = sum(1 for r in all_results if r["confidence"] == "skipped")
    matched = high + low

    accuracy = matched / (total - skipped) if (total - skipped) > 0 else 0.0

    # Per-section accuracy
    section_accuracy = {}
    for key, stats in sorted(section_stats.items()):
        tested = stats["tested"]
        matched_section = stats["high"] + stats["low"]
        section_accuracy[key] = round(matched_section / tested, 4) if tested > 0 else 0.0

    # Build output
    output = {
        "tested_file": os.path.basename(docx_path),
        "tested_at": datetime.now(timezone.utc).isoformat(),
        "ggs_reference": ref_path,
        "threshold": threshold,
        "total_tuks_tested": total,
        "high_confidence": high,
        "low_confidence": low,
        "mismatched": mismatch,
        "skipped": skipped + skipped_no_page,
        "accuracy": round(accuracy, 4),
        "section_accuracy": section_accuracy,
        "discrepancies": discrepancies,
    }

    # Save results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print(f"Gurbani Accuracy Test Results")
    print(f"{'='*60}")
    print(f"File:            {os.path.basename(docx_path)}")
    print(f"Total tuks:      {total}")
    print(f"High confidence: {high} (>= {HIGH_CONFIDENCE})")
    print(f"Low confidence:  {low} ({threshold} - {HIGH_CONFIDENCE})")
    print(f"Mismatched:      {mismatch} (< {threshold})")
    print(f"Skipped:         {skipped + skipped_no_page}")
    print(f"Accuracy:        {accuracy:.1%}")
    print(f"{'='*60}")

    if section_accuracy:
        print(f"\nPer-section accuracy (GGS page ranges):")
        for key, acc in section_accuracy.items():
            bar = "█" * int(acc * 20) + "░" * (20 - int(acc * 20))
            print(f"  {key:>10s}: {bar} {acc:.1%}")

    print(f"\nResults saved to: {output_path}")

    if discrepancies:
        print(f"\nTop 5 discrepancies:")
        for d in sorted(discrepancies, key=lambda x: x["similarity"])[:5]:
            print(f"  GGS p.{d['ggs_page']} | sim={d['similarity']:.2f} | {d['confidence']}")
            print(f"    extracted: {d['tuk'][:70]}")
            print(f"    expected:  {d['best_match'][:70]}")

    # Generate markdown report
    md_path = output_path.replace(".json", ".md")
    generate_md_report(output, md_path)

    return output


def generate_md_report(results: dict, md_path: str) -> None:
    """Generate a markdown report with visual accuracy breakdown."""
    lines = []
    lines.append("# Gurbani Accuracy Test Report\n")
    lines.append(f"**File:** `{results['tested_file']}`  ")
    lines.append(f"**Date:** {results['tested_at'][:10]}  ")
    lines.append(f"**Threshold:** {results['threshold']}\n")

    lines.append("---\n")
    lines.append("## Summary\n")
    total = results["total_tuks_tested"]
    high = results["high_confidence"]
    low = results["low_confidence"]
    mismatch = results["mismatched"]
    skipped = results["skipped"]
    acc = results["accuracy"]

    lines.append(f"| Metric | Count | % |")
    lines.append(f"|--------|-------|---|")
    lines.append(f"| Total tuks tested | {total} | |")
    lines.append(f"| High confidence (>= 0.95) | {high} | {high/total*100:.1f}% |")
    lines.append(f"| Low confidence (0.85-0.95) | {low} | {low/total*100:.1f}% |")
    lines.append(f"| Mismatched (< 0.85) | {mismatch} | {mismatch/total*100:.1f}% |")
    lines.append(f"| Skipped | {skipped} | |")
    lines.append(f"| **Overall accuracy** | **{high+low}** | **{acc:.1%}** |\n")

    lines.append("---\n")
    lines.append("## Per-Section Accuracy (GGS Page Ranges)\n")
    lines.append("| GGS Pages | Accuracy | Visual |")
    lines.append("|-----------|----------|--------|")
    for key, acc_val in sorted(results["section_accuracy"].items(),
                                key=lambda x: int(x[0].split("-")[0])):
        bar = "█" * int(acc_val * 20) + "░" * (20 - int(acc_val * 20))
        lines.append(f"| {key} | {acc_val:.1%} | `{bar}` |")

    lines.append("\n---\n")
    lines.append("## Top Discrepancies (lowest similarity)\n")
    discs = sorted(results["discrepancies"], key=lambda x: x["similarity"])
    for d in discs[:20]:
        lines.append(f"### GGS Page {d['ggs_page']} (PDF Page {d['pdf_page']}) — sim: {d['similarity']:.2f}\n")
        lines.append(f"- **Extracted:** `{d['tuk'][:100]}`")
        lines.append(f"- **Expected:** `{d['best_match'][:100]}`")
        lines.append(f"- **Confidence:** {d['confidence']}\n")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Markdown report saved to: {md_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Gurbani accuracy against GGS reference")
    parser.add_argument("docx", help="Path to the generated docx file")
    parser.add_argument("--ref", default=DEFAULT_REF, help="Path to ggs_reference.json")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output JSON path")
    parser.add_argument("--threshold", type=float, default=DEFAULT_LOW_THRESHOLD,
                        help=f"Lower confidence threshold (default: {DEFAULT_LOW_THRESHOLD})")
    args = parser.parse_args()

    run_accuracy_test(args.docx, args.ref, args.output, args.threshold)
