# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The system has four classes. `Owner` stores the owner's name and pets. `Pet` stores each pet's details and care tasks. `Task` records a description, scheduled time, frequency, completion state, and due date. `Scheduler` retrieves tasks from the owner, filters and sorts them, reports exact-time conflicts, and creates the next occurrence of recurring tasks.

**b. Design changes**

The first design focused on the owner-pet-task relationships. During implementation, tasks gained a due date so future recurring instances could be kept out of today's schedule. Recurrence is handled by `Scheduler.mark_task_complete(pet, task)`, which can both mark the task complete and add its next instance to the pet.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler includes tasks due on or before today, filters out completed tasks by default, can filter by pet name, and sorts by scheduled `HH:MM` time. Daily and weekly tasks recur after completion. Priority, task duration, owner availability, and preferences are not part of the current scheduling algorithm.

**b. Tradeoffs**

Conflict detection checks whether two tasks have the exact same scheduled time and returns a warning. It does not use task duration to find overlapping ranges. Exact matches are easy to explain and let the app flag obvious collisions, while duration-aware overlap detection is a useful next step.

---

## 3. AI Collaboration

**a. How you used AI**

I used the coding assistant to help design the classes, implement the scheduler and Streamlit connection, expand the tests, and draft the documentation. Specific questions about how the scheduler should retrieve owner tasks, how recurring dates should be calculated, and which edge cases to test were most useful because they led to concrete changes that could be checked.

The work was organized into phases, but I kept it in one ongoing chat rather than opening separate chat sessions. Keeping the requests phase-focused made the steps easier to follow; separate chats could also help keep planning, implementation, and testing context independent.

**b. Judgment and verification**

I modified the option of letting `Task.mark_complete()` also create a recurring instance. A task alone cannot add its next instance to the right pet; I put that behavior in `Scheduler.mark_task_complete(pet, task)`, which has access to both objects and can update the pet's task list. I checked this behavior with tests for daily and weekly dates, non-recurring tasks, and repeated completion.

---

## 4. Testing and Verification

**a. What you tested**

The 12 tests cover task completion and addition; chronological sorting and deterministic ties; filtering by pet, completion state, and due date; daily and weekly recurrence; non-recurring and repeated completion; conflicts on the same and different pets; an owner with no tasks; and a Streamlit flow that verifies a submitted task is saved to its pet and appears in the schedule. These cases verify both ordinary use and boundary behavior such as an empty schedule or a future task.

**b. Confidence**

My confidence is **4/5** based on the passing tests and demo. I would next test malformed time values, daylight-saving or timezone expectations, and conflicts between tasks whose durations overlap without sharing an exact start time. The current model does not store duration or persist data after the Streamlit session ends.

---

## 5. Reflection

**a. What went well**

The same scheduler methods power both the terminal demo and the Streamlit app. That made it possible to check sorting, filtering, recurrence, and conflict warnings from two interfaces without duplicating the scheduling rules.

**b. What you would improve**

I would add task duration and use it to detect overlapping time ranges. I would also add ways to edit or remove tasks and persist owner data beyond a single Streamlit session.

**c. Key takeaway**

Being the lead architect meant deciding what the system should do, reviewing whether the generated design matched the actual code, and checking the result with tests. AI helped produce options and implementation quickly, but I still had to choose clear boundaries between classes, document the tradeoffs, and verify behavior before treating the work as complete.
