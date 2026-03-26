# MavAdvisors

A course advising tool for UTA (University of Texas at Arlington) students. It builds a prerequisite/corequisite graph of degree plan courses and recommends optimal semester schedules based on what you've already completed.

Currently defaults to the **B.S. in Computer Science** degree plan.

---

## Project Structure

| File | Description |
|---|---|
| `graph_editor.html` | Visual graph editor for building and editing the course dependency graph. Outputs/imports `cs_course_graph.json`. |
| `mav_advisor.py` | Main CLI advisor. Recommends next-semester courses based on completed coursework. |
| `cs_course.py` | Defines the CS degree plan as a NetworkX directed graph (nodes, edges, metadata) and rules (locked categories, elective slots). |
| `pdf_extract.py` | Parses a selectable-text transcript PDF and extracts normalized course IDs. |
| `cs_course_graph.json` | JSON export of the course graph, used by `graph_editor.html`. |

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **Node/npm** not required — the graph editor is a standalone HTML file

### Install Python Dependencies

```bash
pip install networkx pdfplumber
```

---

## Usage

### Graph Editor (`graph_editor.html`)

The graph editor is a standalone HTML page for visually creating and editing the course prerequisite graph.

1. Open `graph_editor.html` with **Live Server** in VS Code (right-click the file → "Open with Live Server").
2. Add/remove course nodes, set metadata (name, credits, category), and draw prerequisite or corequisite edges.
3. Export the graph to `cs_course_graph.json` or import an existing one.

### Course Advisor (`mav_advisor.py`)

The advisor recommends your next semester's courses. It reads the degree plan graph and rules from `cs_course.py` and gives you up to three schedule options with different gen-ed balances.

```bash
python mav_advisor.py
```

You'll be prompted to choose:

1. **New or Old student**
   - **New** — starts with no completed courses.
   - **Old** — provide your completed courses via one of two methods:
     - **(1) Upload a transcript PDF** — uses `pdf_extract.py` to parse course IDs from a selectable-text transcript.
     - **(2) Type/paste courses** — enter course IDs separated by spaces or commas (e.g. `cse1310, math1426, engl1301`).

2. **Target credits** — how many credit hours you want next semester (e.g. 12, 15, 17).

The advisor then outputs up to three recommended schedules:
- **No Gen Ed** — prioritizes major courses only.
- **One Gen Ed (Recommended)** — balanced mix.
- **Two Gen Ed** — lighter major load.

#### Using a Different Degree Plan

The advisor is major-agnostic. To use a different plan module:

```bash
python mav_advisor.py --plan ce_course
```

The plan module must define `build_graph() -> nx.DiGraph` and `get_rules() -> dict`.

### Transcript Parser (`pdf_extract.py`)

Can also be run standalone to inspect what courses are extracted from a transcript:

```bash
python pdf_extract.py "path/to/transcript.pdf"
```

The PDF must contain selectable text (not a scanned image).

---

## How It Works

- **`cs_course.py`** builds a NetworkX `DiGraph` where each node is a course with metadata (`name`, `credits`, `category`) and edges represent `prereq` or `coreq` relationships. It also defines rules for category locking (e.g. professional courses are locked until all pre-professional courses are complete) and elective slot management (tech electives, security electives, gen-ed sub-groups).

- **`mav_advisor.py`** loads the graph and rules, determines which courses are eligible based on completed prerequisites/corequisites and lock rules, scores each eligible course (by how many downstream courses it unlocks, category priority, and credit fit), and greedily builds semester plans up to the target credit count.

- **`pdf_extract.py`** uses `pdfplumber` to extract text line-by-line, matches course codes via regex (`DEPT 1234` patterns), filters out date/term lines, deduplicates, and returns normalized IDs (e.g. `cse1310`).
