# TaskFlow — AI-Assisted Task Management Platform

A full-stack task-and-project management platform built for Blinkit's dark-store engineering pods. Teams organize work into projects, track individual tasks, see progress statistics, sort and search through task lists, and use an AI-assisted quick-add feature that converts plain English into structured task records.

Built with **FastAPI + SQLAlchemy** (backend) and **vanilla HTML/CSS/JS** (frontend dashboard).

---

## Table of Contents

1. [Repository Structure](#repository-structure)
2. [Environment Setup](#environment-setup)
3. [Running the App](#running-the-app)
4. [Endpoint Reference](#endpoint-reference)
5. [Algorithms Engine (Section 2)](#algorithms-engine-section-2)
6. [AI Quick-Add (Section 3)](#ai-quick-add-section-3)

---

## Repository Structure

```
taskflow/
├── backend/
│   ├── main.py            # FastAPI app: all endpoints, middleware, CORS
│   ├── database.py        # SQLAlchemy engine, session, get_db dependency
│   ├── models.py          # ORM models: User, Project, Task
│   ├── schemas.py         # Pydantic models with field constraints & validators
│   ├── algorithms.py      # insertion_sort, binary_search, linear_search + counting wrappers
│   ├── ai_parser.py       # Mock LLM parser (rule-based, zero API keys)
│   ├── seed.py            # Seeds the database with sample data
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── index.html         # Semantic HTML dashboard
│   ├── styles.css         # Box model, 2 breakpoints, sticky positioning
│   └── script.js          # Fetch API, safe DOM rendering, localStorage cache
├── check_algorithms.py    # PASS/FAIL automated checks (Section 2, Task 7)
├── benchmark.py           # Comparison-counting benchmark (Section 2, Tasks 5-6)
├── results.txt            # Saved benchmark output
└── README.md              # This file
```

---

## Environment Setup

### 1. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r backend/requirements.txt
```

This installs: `fastapi`, `uvicorn[standard]`, `sqlalchemy`, `pydantic`.

---

## Running the App

This project uses the **two-process run** (recommended): the backend runs on port 8000, and the frontend is served on port 5500.

### Step 1: Start the backend

```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API is now available at `http://127.0.0.1:8000`. Interactive docs at `http://127.0.0.1:8000/docs`.

### Step 2: Seed the database (optional, for sample data)

In a new terminal:

```bash
cd backend
python3 seed.py
```

This creates 2 users, 2 projects, and 8 sample tasks.

### Step 3: Start the frontend

In a new terminal:

```bash
cd frontend
python3 -m http.server 5500 --bind 127.0.0.1
```

Open `http://127.0.0.1:5500` in your browser. The dashboard loads tasks from the backend and lets you add, edit, delete, sort, search, and quick-add tasks.

### CORS note

The backend's CORS configuration explicitly allows `http://127.0.0.1:5500` and `http://localhost:5500` (the frontend's origin), with allowed methods and headers listed explicitly.

---

## Endpoint Reference

Full list of all endpoints with example request bodies and responses.

### Users

#### Create User — `POST /users`

**Request:**
```json
{ "email": "alice@blinkit.com", "name": "Alice Sharma" }
```

**Response (201):**
```json
{ "id": 1, "email": "alice@blinkit.com", "name": "Alice Sharma" }
```

#### List Users — `GET /users`

**Response (200):**
```json
[
  { "id": 1, "email": "alice@blinkit.com", "name": "Alice Sharma" },
  { "id": 2, "email": "bob@blinkit.com", "name": "Bob Verma" }
]
```

#### Get User by ID — `GET /users/{user_id}`

**Response (200):**
```json
{ "id": 1, "email": "alice@blinkit.com", "name": "Alice Sharma" }
```

**Failure (404):** `{"detail": "User not found"}`

---

### Projects

#### Create Project — `POST /projects`

**Request:**
```json
{ "name": "Dark Store Dashboard", "description": "Ops dashboard", "owner_id": 1 }
```

**Response (201):**
```json
{ "id": 1, "name": "Dark Store Dashboard", "description": "Ops dashboard", "owner_id": 1 }
```

#### List Projects — `GET /projects`

**Response (200):**
```json
[
  { "id": 1, "name": "Dark Store Dashboard", "description": "Ops dashboard", "owner_id": 1 }
]
```

#### Get Project by ID — `GET /projects/{project_id}`

**Response (200):**
```json
{ "id": 1, "name": "Dark Store Dashboard", "description": "Ops dashboard", "owner_id": 1 }
```

**Failure (404):** `{"detail": "Project not found"}`

---

### Tasks — CRUD

#### Create Task — `POST /tasks`

**Request:**
```json
{
  "title": "Fix checkout bug",
  "priority": "high",
  "status": "pending",
  "due_date": "tomorrow",
  "project_id": 1
}
```

**Response (201):**
```json
{
  "id": 10,
  "title": "Fix checkout bug",
  "priority": "high",
  "status": "pending",
  "due_date": "tomorrow",
  "project_id": 1
}
```

**Failure (422 — invalid priority):**
```json
{
  "detail": [{ "type": "pattern_match", "loc": ["body", "priority"], "msg": "..." }]
}
```

**Failure (422 — blank title):**
```json
{
  "detail": [{ "type": "value_error", "loc": ["body", "title"], "msg": "title must not be blank or whitespace-only" }]
}
```

#### List Tasks — `GET /tasks`

**Response (200):**
```json
[
  { "id": 1, "title": "Design login page", "priority": "high", "status": "done", "due_date": "today", "project_id": 1 }
]
```

#### Get Task by ID — `GET /tasks/{task_id}`

**Response (200):**
```json
{ "id": 1, "title": "Design login page", "priority": "high", "status": "done", "due_date": "today", "project_id": 1 }
```

**Failure (404):** `{"detail": "Task not found"}`

#### Update Task — `PUT /tasks/{task_id}`

**Request:**
```json
{ "status": "done", "priority": "high" }
```

**Response (200):**
```json
{ "id": 1, "title": "Design login page", "priority": "high", "status": "done", "due_date": "today", "project_id": 1 }
```

**Failure (404):** `{"detail": "Task not found"}`

#### Delete Task — `DELETE /tasks/{task_id}`

**Response (204):** No content.

**Failure (404):** `{"detail": "Task not found"}`

---

### Statistics

#### Project Stats — `GET /projects/{project_id}/stats`

Returns per-project task statistics computed with SQL `COUNT` and `GROUP BY` across a join of projects and tasks (aggregation happens in the query, not in Python).

**Response (200):**
```json
{
  "project_id": 1,
  "project_name": "Dark Store Dashboard",
  "total_tasks": 5,
  "pending": 2,
  "in_progress": 1,
  "done": 2
}
```

---

### Sorted List

#### Sort Tasks — `GET /tasks?sort=priority`

Fetches tasks from the database into a list of dicts, maps priority to a rank (low=1, medium=2, high=3), then calls `insertion_sort` on the list. The ordering is produced by our own function, not by SQL `ORDER BY` or Python's `sorted()`.

**Response (200):**
```json
[
  { "id": 3, "title": "Write API documentation", "priority": "low", "status": "pending", "due_date": "next friday", "project_id": 1 },
  { "id": 2, "title": "Build task list component", "priority": "medium", "status": "in_progress", "due_date": "tomorrow", "project_id": 1 },
  { "id": 1, "title": "Design login page", "priority": "high", "status": "done", "due_date": "today", "project_id": 1 }
]
```

Also supports `GET /tasks?sort=due_date` — sorts by the `due_date` text field using `insertion_sort`.

---

### Search

#### Search Task — `GET /tasks/search?title=<exact title>&algo=binary|linear`

Builds an in-memory index of `{"id": ..., "title": ...}` pairs from real database tasks. When `algo=binary` (default), sorts the index by title with `insertion_sort` then calls `binary_search`. When `algo=linear`, calls `linear_search` on the unsorted index.

**Response (200):**
```json
{ "id": 1, "title": "Design login page", "priority": "high", "status": "done", "due_date": "today", "project_id": 1 }
```

**Failure (404):** `{"detail": "Task not found"}`

---

### Quick-Add (AI)

#### Quick-Add Task — `POST /tasks/quick-add`

Accepts a free-text description and creates a real task row using the deterministic mock parser.

**Request:**
```json
{ "description": "Finish the report next Friday, it's urgent", "project_id": 1 }
```

**Response (201):**
```json
{
  "id": 11,
  "title": "Finish the report , it's",
  "priority": "high",
  "status": "pending",
  "due_date": "next friday",
  "project_id": 1
}
```

**Failure (422 — non-existent project_id):**
```json
{ "detail": "project_id does not reference an existing project" }
```

**Failure (422 — blank description):**
```json
{ "detail": "description must not be blank" }
```

---

## Algorithms Engine (Section 2)

### Implemented Functions

All three functions are in `backend/algorithms.py`. They do **not** use Python's `sorted()`, `list.sort()`, or any built-in search.

#### `insertion_sort(records, key)`

Sorts a list of dictionaries in place by `record[key]`. Standard insertion-sort structure: starts from the second element, compares against previous elements, shifts to insert into correct position. Mutates the list directly; returns `None`.

#### `binary_search(sorted_records, target_value, key)`

Operates on a list already sorted by `key`. Uses the standard `low`/`high`/`mid` pointer structure. Returns the index of a matching record, or `-1` if not found.

#### `linear_search(records, target_value, key)`

Baseline scan: iterates every record in order. Returns the index of the first match, or `-1` if not found.

### How They Power the Endpoints

- **`GET /tasks?sort=priority`** — fetches all tasks from the database into a list of dicts, maps priority to a rank (low=1, medium=2, high=3), then calls `insertion_sort(records, "priority_rank")`.
- **`GET /tasks/search?title=...&algo=binary`** — builds an index of `{"id", "title"}` pairs from real tasks, sorts it with `insertion_sort`, then calls `binary_search`.
- **`GET /tasks/search?title=...&algo=linear`** — calls `linear_search` on the unsorted index.

### Time Complexity

| Algorithm | Best Case | Worst Case |
|---|---|---|
| Insertion Sort | O(n) — already sorted | O(n²) — reverse sorted |
| Binary Search | O(1) — target at mid | O(log n) |
| Linear Search | O(1) — target at first position | O(n) — target at last or absent |

### Benchmark Results

Run with: `python3 benchmark.py`

The counting-wrapper functions (`insertion_sort_count`, `binary_search_count`, `linear_search_count`) re-implement the same logic while counting comparisons. Synthetic task dictionaries use the exact same fields (title, priority, due_date) as the real task model.

**Saved benchmark output (from `results.txt`):**

| Size | insertion_sort | binary_search (hit) | binary_search (miss) | linear_search (hit) | linear_search (miss) |
|------|---------------|--------------------|--------------------|--------------------|--------------------|
| 10 | 21 comparisons | 3 comparisons | 4 comparisons | 6 comparisons | 10 comparisons |
| 500 | 44,240 comparisons | 8 comparisons | 9 comparisons | 251 comparisons | 500 comparisons |
| 3,000 | 1,543,842 comparisons | 11 comparisons | 12 comparisons | 1,501 comparisons | 3,000 comparisons |

### Is Sorting First Worth It?

The counted numbers show that a single insertion sort at 3,000 tasks costs ~1.5M comparisons, while a single linear search costs at most 3,000 — so for a one-off search, linear search is cheaper. But TaskFlow teams **list and sort their tasks repeatedly** throughout the day (every page load, every sort-selection change), while they **add or rename tasks relatively infrequently**. Once the list is sorted (one O(n²) cost), every subsequent search is binary and costs only ~11 comparisons regardless of list size. Over a workday with, say, 50 searches on a 3,000-task list, linear search totals 150,000 comparisons while binary search totals 550 — a 270x reduction. The sort cost is paid once and amortized across all those searches, making sort-first clearly worth it for this usage pattern. The one caveat is that the list must be re-sorted after each insert/rename; given that edits are far less frequent than searches, the trade-off favors keeping the list sorted.

### Automated Checks

Run with: `python3 check_algorithms.py`

```
PASS: insertion_sort empty list
PASS: insertion_sort single element
PASS: binary_search first index
PASS: binary_search last index
PASS: binary_search middle index
PASS: binary_search not found
PASS: insertion_sort_count sorts correctly
PASS: insertion_sort_count returns int > 0
PASS: binary_search_count correct index
PASS: binary_search_count comparison_count is int > 0
PASS: linear_search_count absent index
PASS: linear_search_count absent comparison_count equals length
```

---

## AI Quick-Add (Section 3)

### Prompting Technique Rationale (300 words)

The system message and mock logic use a **zero-shot** prompting technique. The system-role instruction describes the parsing behavior in a single directive — extract title, priority, and due_date_hint, strip keywords, and fall back to "Untitled task" — without providing any example input-output pairs (which would make it few-shot) or asking the model to reason step-by-step (which would make it chain-of-thought).

Zero-shot is the right choice for this feature for two reasons. First, **token usage**: the system message is a single compact paragraph, and the user message is just the raw description. Few-shot examples would multiply the input tokens by 3-5x for each example, and chain-of-thought would add reasoning tokens to every response — both expensive for a feature that runs on every quick-add. Second, **response reliability**: the task is a deterministic extraction with a closed output schema (priority is one of three values, due_date_hint is a known phrase or null). Zero-shot with a clear system instruction produces consistent structured output for this kind of bounded parsing task, where the complexity does not warrant chain-of-thought decomposition. The mock parser mirrors this by applying the same rules deterministically, ensuring identical output whether or not a real LLM is present.

### Mock Parser Algorithm

The parser (`backend/ai_parser.py`) follows the exact algorithm from the spec:

1. **Lower-case working copy** for keyword matching; original-cased description kept for title extraction.
2. **Priority** — checks in order: "urgent"/"asap" → high; "whenever"/"low priority" → low; else medium.
3. **Due-date hint** — checks in order: "today", "tomorrow", "next week", "next monday"–"next sunday" (as whole two-word phrases), bare "monday"–"sunday". First match wins.
4. **Title** — removes every occurrence of all matched priority keywords and all matched date phrases from the original-cased text. Strips whitespace. If empty, uses "Untitled task".

The function runs with **zero network calls and zero API keys**.

### Five Worked Examples

#### Example 1
**Input:** `"Review the urgent deployment tomorrow"`
**Parsed output:**
```json
{ "title": "Review the  deployment", "priority": "high", "due_date_hint": "tomorrow" }
```
*Priority is "high" (contains "urgent"); "tomorrow" matched as date; both "urgent" and "tomorrow" stripped from title.*

#### Example 2
**Input:** `"Low priority cleanup whenever you have time"`
**Parsed output:**
```json
{ "title": "cleanup  you have time", "priority": "low", "due_date_hint": null }
```
*Priority is "low" (contains "low priority" and "whenever"); both keywords stripped from title; no date match.*

#### Example 3
**Input:** `"Prepare slides for next monday presentation"`
**Parsed output:**
```json
{ "title": "Prepare slides for  presentation", "priority": "medium", "due_date_hint": "next monday" }
```
*"next monday" matched as a two-word phrase; stripped from title; no priority keywords → medium.*

#### Example 4
**Input:** `"Fix the login bug ASAP"`
**Parsed output:**
```json
{ "title": "Fix the login bug", "priority": "high", "due_date_hint": null }
```
*Priority is "high" (contains "asap"); "asap" stripped from title; no date match.*

#### Example 5
**Input:** `"Team meeting friday"`
**Parsed output:**
```json
{ "title": "Team meeting", "priority": "medium", "due_date_hint": "friday" }
```
*"friday" matched as bare weekday; stripped from title; no priority keywords → medium.*

### Spec Worked Examples (verified)

These are the four examples from the spec, verified against the running mock:

| # | Input | title | priority | due_date_hint |
|---|-------|-------|----------|---------------|
| 1 | `"This is urgent, mark it ASAP please"` | `"This is , mark it  please"` | `"high"` | `null` |
| 2 | `" "` (whitespace only) | `"Untitled task"` | `"medium"` | `null` |
| 3 | `"Finish the report next Friday, it's urgent"` | `"Finish the report , it's"` | `"high"` | `"next friday"` |
| 4 | `"tomorrow review tomorrow"` | `"review"` | `"medium"` | `"tomorrow"` |

### Optional Real-LLM Path

The code is structured to support an optional real LLM call behind an environment variable `USE_REAL_LLM` (defaults to unset/false). The `build_prompt()` function constructs the standard role-based message list (system + user). When the flag is off or no API key is present, the endpoint uses the mock parser automatically. Grading is always performed with the flag off — no paid service is required.

### Validation Before Persistence

Whatever the parser produces is validated against the Pydantic `TaskCreate` model before being written to the database. If validation fails (missing description, non-existent project_id, or malformed body), the endpoint returns HTTP 422 with validation error detail and no row is created.

---

## Database Schema

Three tables with primary keys, foreign keys, and constraints:

```
users
  id          INTEGER PRIMARY KEY
  email       TEXT NOT NULL UNIQUE
  name        TEXT NOT NULL

projects
  id          INTEGER PRIMARY KEY
  name        TEXT NOT NULL
  description TEXT (nullable)
  owner_id    INTEGER NOT NULL → users.id (FOREIGN KEY)

tasks
  id          INTEGER PRIMARY KEY
  title       TEXT NOT NULL
  priority    TEXT NOT NULL (low | medium | high)
  status      TEXT NOT NULL (pending | in_progress | done)
  due_date    TEXT (nullable — stores raw text, not a strict date type)
  project_id  INTEGER NOT NULL → projects.id (FOREIGN KEY)
```

Relationships are wired with `relationship()` and `back_populates` on both sides:
- `User.projects` ↔ `Project.owner`
- `Project.tasks` ↔ `Task.project`

---

## Architecture Notes

- **Dependency function**: `get_db()` in `database.py` is used in every endpoint signature via `Depends(get_db)` — written once, reused everywhere.
- **Middleware**: Custom HTTP middleware logs the method, path, and processing time (ms) for every request to the console.
- **CORS**: Explicitly allows `http://127.0.0.1:5500` and `http://localhost:5500` with methods and headers listed.
- **Frontend rendering**: Uses `document.createElement()` and `appendChild()` with `textContent` for all user-provided text — no `innerHTML` for user data.
- **localStorage cache**: Tasks are cached as JSON on every change and rendered from cache on page load while the live backend request is in flight.
