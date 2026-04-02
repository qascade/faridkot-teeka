"""
download_ggs_reference.py — One-time download of all 1430 GGS pages from GurbaniDB API.

Supports both Gurmukhi and Devanagari scripts:
  python3 download_ggs_reference.py                    # Gurmukhi (default)
  python3 download_ggs_reference.py --devanagari       # Devanagari

Saves to gurbani_accuracy_test/data/ggs_reference.json (Gurmukhi)
     or gurbani_accuracy_test/data/ggs_reference_devanagari.json (Devanagari)

Idempotent: skips if file already exists unless --force is passed.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

TOTAL_PAGES = 1430
API_BASE = "http://api.sikher.com/page"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# API language IDs
DEVANAGARI_TRANSLITERATION_ID = 59
ENGLISH_TRANSLATION_ID = 13


def fetch_page(page_num: int, devanagari: bool = False) -> tuple[int, list[str]]:
    """Fetch a single GGS page from the API. Retries once on failure."""
    if devanagari:
        url = f"{API_BASE}/{page_num}/{ENGLISH_TRANSLATION_ID}/{DEVANAGARI_TRANSLITERATION_ID}"
    else:
        url = f"{API_BASE}/{page_num}"
    for attempt in range(2):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if devanagari:
                lines = [
                    entry["transliteration"]["text"]
                    for entry in data
                    if entry.get("transliteration") and entry["transliteration"].get("text")
                ]
            else:
                lines = [entry["text"] for entry in data if "text" in entry]
            return page_num, lines
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            if attempt == 0:
                continue
            raise RuntimeError(f"Failed to fetch page {page_num} after 2 attempts: {e}")


def validate_reference(ref: dict[str, list[str]]) -> None:
    """Validate the downloaded reference data. Raises ValueError on failure."""
    missing = [str(p) for p in range(1, TOTAL_PAGES + 1) if str(p) not in ref]
    if missing:
        raise ValueError(f"Missing {len(missing)} pages: {', '.join(missing[:10])}...")

    empty_pages = [p for p, lines in ref.items() if not lines]
    if empty_pages:
        raise ValueError(f"{len(empty_pages)} pages have no lines: {', '.join(empty_pages[:10])}...")

    empty_lines = []
    for p, lines in ref.items():
        for i, line in enumerate(lines):
            if not line.strip():
                empty_lines.append(f"page {p} line {i}")
    if empty_lines:
        raise ValueError(f"{len(empty_lines)} empty lines found: {', '.join(empty_lines[:10])}...")


def download(force: bool = False, devanagari: bool = False) -> None:
    script_name = "Devanagari" if devanagari else "Gurmukhi"
    suffix = "_devanagari" if devanagari else ""
    output_path = os.path.join(SCRIPT_DIR, "data", f"ggs_reference{suffix}.json")

    if os.path.exists(output_path) and not force:
        print(f"{script_name} reference already exists: {output_path}")
        print("Use --force to re-download.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Downloading {TOTAL_PAGES} GGS pages ({script_name}) from {API_BASE}...")
    reference: dict[str, list[str]] = {}
    completed = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_page, p, devanagari): p
            for p in range(1, TOTAL_PAGES + 1)
        }
        for future in as_completed(futures):
            page_num = futures[future]
            try:
                pn, lines = future.result()
                reference[str(pn)] = lines
                completed += 1
                if completed % 100 == 0 or completed == TOTAL_PAGES:
                    print(f"  {completed}/{TOTAL_PAGES} pages downloaded")
            except Exception as e:
                print(f"ERROR on page {page_num}: {e}", file=sys.stderr)
                sys.exit(1)

    print("Validating reference data...")
    try:
        validate_reference(reference)
    except ValueError as e:
        print(f"VALIDATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)

    # Sort by page number for readability
    sorted_ref = {str(p): reference[str(p)] for p in range(1, TOTAL_PAGES + 1)}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sorted_ref, f, ensure_ascii=False, indent=2)

    total_lines = sum(len(lines) for lines in sorted_ref.values())
    print(f"\nSaved {TOTAL_PAGES} pages ({total_lines} lines) to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download GGS reference from GurbaniDB API")
    parser.add_argument("--force", action="store_true", help="Re-download even if cached")
    parser.add_argument("--devanagari", action="store_true", help="Download Devanagari transliteration")
    args = parser.parse_args()
    download(force=args.force, devanagari=args.devanagari)
