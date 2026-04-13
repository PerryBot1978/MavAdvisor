# pdf_extract.py
# Extract normalized course IDs from a selectable-text transcript PDF.
#
# Usage (standalone):
#   pip install pdfplumber
#   python pdf_extract.py "path/to/transcript.pdf"
#
# Usage (imported):
#   from pdf_extract import parse_transcript_pdf, parse_in_progress_courses
#   courses = parse_transcript_pdf("transcript.pdf")
#   in_progress = parse_in_progress_courses("transcript.pdf")

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

import pdfplumber

# Only match valid-looking course codes
COURSE_RE = re.compile(r"\b([A-Z]{2,6})\s*[- ]?\s*([1-9]\d{3}[A-Z]?)\b")
MONTH_RE = re.compile(r"\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|SEPT|OCT|NOV|DEC)\b", re.IGNORECASE)

# Valid final letter grades
GRADE_RE = re.compile(r"\b(A|B|C|D|F)\b(?:[+-])?", re.IGNORECASE)


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


def has_grade(line: str) -> bool:
    return GRADE_RE.search(line) is not None


def parse_transcript_details(pdf_path: str) -> Tuple[List[str], List[str]]:
    """
    Returns:
        completed_courses: courses with a valid letter grade
        courses_in_progress: courses found without a valid letter grade
    """
    lines = extract_lines(pdf_path)

    completed_courses: List[str] = []
    courses_in_progress: List[str] = []

    for line in lines:
        # Skip term/date lines like "AUG 2021"
        if MONTH_RE.search(line):
            continue

        course = parse_course(line)
        if not course:
            continue

        if has_grade(line):
            completed_courses.append(course)
        else:
            courses_in_progress.append(course)

    # de-dupe while preserving order
    def dedupe(items: List[str]) -> List[str]:
        seen = set()
        out: List[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                out.append(item)
        return out

    return dedupe(completed_courses), dedupe(courses_in_progress)


def parse_transcript_pdf(pdf_path: str) -> List[str]:
    completed_courses, _ = parse_transcript_details(pdf_path)
    return completed_courses


def parse_in_progress_courses(pdf_path: str) -> List[str]:
    _, courses_in_progress = parse_transcript_details(pdf_path)
    return courses_in_progress


def main() -> None:
    pdf_path = Path("transcript.pdf")
    if not pdf_path.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    completed, in_progress = parse_transcript_details(pdf_path)

    if not completed and not in_progress:
        print("No courses found. If this is a scanned PDF, selectable text will not extract.")
        return

    print("COMPLETED COURSES:")
    for c in completed:
        print(c)

    print("\nCOURSES IN PROGRESS:")
    for c in in_progress:
        print(c)


if __name__ == "__main__":
    main()