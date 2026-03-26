# pdf_extract.py
# Extract normalized course IDs from a selectable-text transcript PDF.
#
# Usage (standalone):
#   pip install pdfplumber
#   python pdf_extract.py "path/to/transcript.pdf"
#
# Usage (imported):
#   from pdf_extract import parse_transcript_pdf
#   courses = parse_transcript_pdf("transcript.pdf")

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

import pdfplumber

# Only match valid-looking course codes (avoids years like 2021)
COURSE_RE = re.compile(r"\b([A-Z]{2,6})\s*[- ]?\s*([1-9]\d{3}[A-Z]?)\b")
MONTH_RE = re.compile(r"\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|SEPT|OCT|NOV|DEC)\b", re.IGNORECASE)


def extract_lines(pdf_path: str) -> List[str]:
    lines: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for ln in text.splitlines():
                ln = ln.strip()
                if ln:
                    lines.append(ln)
    return lines


def normalize_course(dept: str, number: str) -> str:
    return f"{dept}{number}".lower().replace(" ", "").replace("-", "").replace("_", "")


def parse_course(line: str) -> str | None:
    cm = COURSE_RE.search(line)
    if not cm:
        return None
    return normalize_course(cm.group(1), cm.group(2))


def parse_transcript_pdf(pdf_path: str) -> List[str]:
    lines = extract_lines(pdf_path)

    courses: List[str] = []
    for line in lines:
        # Skip term/date lines like "AUG 2021"
        if MONTH_RE.search(line):
            continue

        course = parse_course(line)
        if course:
            courses.append(course)

    # de-dupe while preserving order
    seen = set()
    out: List[str] = []
    for c in courses:
        if c not in seen:
            seen.add(c)
            out.append(c)

    return out


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python pdf_extract.py "path/to/transcript.pdf"')
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    out = parse_transcript_pdf(pdf_path)
    if not out:
        print("No courses found. If this is a scanned PDF, selectable text will not extract.")
        return

    print("COURSES FOUND:")
    for c in out:
        print(c)


if __name__ == "__main__":
    main()
