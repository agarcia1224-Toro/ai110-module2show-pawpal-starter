"""Tests for PawPal+ task and scheduling behavior."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_task_status() -> None:
    """A task becomes completed after mark_complete is called."""
    task = Task("Feed", "08:00")
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count() -> None:
    """Adding a task stores it on the pet."""
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "08:00"))
    assert len(pet.tasks) == 1


def test_schedule_sorts_by_time_and_filters_by_pet_and_status() -> None:
    """The scheduler returns due incomplete tasks in time order for a pet."""
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    mochi.add_task(Task("Walk", "09:00"))
    mochi.add_task(Task("Breakfast", "07:00"))
    luna.add_task(Task("Medication", "08:00"))
    mochi.tasks[0].mark_complete()
    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler()
    schedule = scheduler.get_schedule(owner)
    assert [task.description for _, task in schedule] == ["Breakfast", "Medication"]
    assert [pet.name for pet, _ in scheduler.filter_tasks(owner, pet_name="lUnA")] == ["Luna"]
    assert [task.description for _, task in scheduler.filter_tasks(owner, completed=True)] == ["Walk"]


def test_completing_recurring_task_creates_next_occurrence() -> None:
    """Daily and weekly tasks recur after one and seven days respectively."""
    pet = Pet("Mochi", "dog")
    task = Task("Walk", "08:00", "daily", due_date=date(2026, 10, 11))
    pet.add_task(task)

    next_task = Scheduler().mark_task_complete(pet, task, completed_on=date(2026, 10, 11))

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == date(2026, 10, 12)
    assert next_task.completed is False
    assert len(pet.tasks) == 2


def test_weekly_task_repeats_after_seven_days() -> None:
    """A weekly task is recreated for the following week."""
    pet = Pet("Luna", "cat")
    task = Task("Medication", "08:00", "weekly", due_date=date(2026, 10, 11))
    pet.add_task(task)

    next_task = Scheduler().mark_task_complete(pet, task, completed_on=date(2026, 10, 11))

    assert next_task is not None
    assert next_task.due_date == date(2026, 10, 18)


def test_conflict_detection_warns_for_exact_time_matches() -> None:
    """Tasks with the same time produce a warning instead of an exception."""
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    tasks = [
        (mochi, Task("Walk", "08:00")),
        (luna, Task("Medication", "08:00")),
        (luna, Task("Dinner", "18:00")),
    ]

    warnings = Scheduler().detect_conflicts(tasks)

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Mochi" in warnings[0]
    assert "Walk" in warnings[0]
