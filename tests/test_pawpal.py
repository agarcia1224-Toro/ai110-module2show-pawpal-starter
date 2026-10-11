"""Basic tests for PawPal+ task and pet behavior."""

from pawpal_system import Pet, Task


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
