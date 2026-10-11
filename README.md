# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## Features

- Add an owner, pets, and pet care tasks in the Streamlit app. Data stays in `st.session_state` for the active session.
- Open a dedicated tab for each pet to see its profile and complete care list, including future recurring tasks and completion status.
- View due, incomplete tasks in chronological `HH:MM` order, with an optional pet filter.
- See a warning when two due tasks have the same scheduled time, including the time and task names.
- Mark tasks complete; daily and weekly tasks create their next occurrence automatically.
- Run a command-line demo with `python main.py` or the automated tests with `python -m pytest`.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run PawPal+

Start the Streamlit app with `streamlit run app.py`. To see the terminal demonstration, run `python main.py`.

### Project files

- `app.py` contains the Streamlit interface.
- `pawpal_system.py` contains the `Owner`, `Pet`, `Task`, and `Scheduler` classes.
- `main.py` runs the command-line demonstration.
- `tests/test_pawpal.py` contains the automated tests.
- [Final class diagram](diagrams/uml_final.mmd) shows the implemented classes and relationships.

## 🧪 Testing PawPal+

```bash
python -m pytest
```

The suite checks task completion and addition; chronological sorting, including ties; filtering by pet, completion status, and due date; daily and weekly recurrence; non-recurring and repeated completion; exact-time conflicts for the same or different pets; empty schedules; and a Streamlit UI flow that verifies an added task is saved and shown in the schedule.

Successful run:

```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\creep\ITC395-Projects\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1, platformdirs-4.12.2
collected 12 items

tests\test_app_ui.py .                                                   [  8%]
tests\test_pawpal.py ...........                                         [100%]

============================= 12 passed in 2.35s ==============================
```

**Confidence level:** ★★★★☆ (4/5). The core scheduling paths and key edge cases pass. Conflict checks only detect exact time matches; duration overlaps are not tested or handled yet.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks chronologically by `HH:MM`, then by pet name and task description. |
| Filtering | `Scheduler.filter_tasks()` | Filters by pet name (case-insensitive), completion status, and due date. |
| Conflict handling | `Scheduler.detect_conflicts()` | Returns warnings for exact time matches across any pets; it does not calculate duration overlaps. |
| Recurring tasks | `Scheduler.mark_task_complete()` | Completing a daily or weekly task creates the next occurrence one or seven days after completion. |

## Demo Walkthrough

1. Enter the owner's name and add pets with their species and optional details. Each pet gets a tab with its profile and full care schedule.
2. Add a care task for a pet, including its description, scheduled time, and frequency.
3. Review today's due tasks. PawPal+ filters out completed and future tasks, sorts the rest by time, and lets you filter the list by pet.
4. If two tasks share a time, the app shows a warning naming the time and tasks and suggests moving one. The first version checks exact time matches, not duration overlaps.
5. Mark a task complete. Daily and weekly tasks are recreated for the next day or week; completed tasks remain available in the completed list.

The terminal demo (`python main.py`) demonstrates sorting, pet filtering, conflict warnings, and recurrence:

```text
Today's Schedule for Jordan:
  07:30 | Mochi: Breakfast (daily)
  08:00 | Luna: Medication (weekly)
  08:00 | Mochi: Morning walk (daily)
  18:00 | Luna: Refresh water (as needed)

Conflict warnings:
Warning: conflict at 08:00: Luna - Medication; Mochi - Morning walk.

Luna's tasks:
  08:00 | Luna: Medication
  18:00 | Luna: Refresh water

Recurring task: Breakfast is next due 2026-10-12 at 07:30.
```
