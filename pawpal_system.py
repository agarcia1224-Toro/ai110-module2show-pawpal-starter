"""Core data models and scheduling behavior for PawPal+."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """Represent one care activity for a pet."""

    description: str
    time: str
    frequency: str = "daily"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False


@dataclass
class Pet:
    """Store a pet's details and care tasks."""

    name: str
    species: str
    breed: str = ""
    age: int | None = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task if it belongs to this pet."""
        self.tasks.remove(task)


@dataclass
class Owner:
    """Manage an owner's pets and provide access to their tasks."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's care."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task paired with the pet it belongs to."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Retrieve, organize, and format tasks across an owner's pets."""

    def get_tasks(self, owner: Owner, include_completed: bool = False) -> list[tuple[Pet, Task]]:
        """Collect the owner's tasks, excluding completed tasks by default."""
        tasks = owner.get_all_tasks()
        if not include_completed:
            tasks = [(pet, task) for pet, task in tasks if not task.completed]
        return tasks

    def get_schedule(self, owner: Owner, include_completed: bool = False) -> list[tuple[Pet, Task]]:
        """Sort tasks by their scheduled time, then pet and description."""
        tasks = self.get_tasks(owner, include_completed)
        return sorted(
            tasks,
            key=lambda item: (
                self._time_sort_key(item[1].time),
                item[0].name.casefold(),
                item[1].description.casefold(),
            ),
        )

    def format_schedule(self, owner: Owner) -> str:
        """Format today's incomplete tasks as a readable terminal schedule."""
        schedule = self.get_schedule(owner)
        if not schedule:
            return f"Today's Schedule for {owner.name}:\n  No tasks scheduled."
        lines = [f"Today's Schedule for {owner.name}:"]
        for pet, task in schedule:
            lines.append(f"  {task.time} | {pet.name}: {task.description} ({task.frequency})")
        return "\n".join(lines)

    @staticmethod
    def _time_sort_key(value: str) -> tuple[int, str]:
        """Sort valid HH:MM times chronologically and other labels afterward."""
        try:
            return (0, datetime.strptime(value, "%H:%M").strftime("%H:%M"))
        except ValueError:
            return (1, value.casefold())
