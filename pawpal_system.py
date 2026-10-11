"""Core data models and scheduling behavior for PawPal+."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta


@dataclass
class Task:
    """Represent one care activity for a pet."""

    description: str
    time: str
    frequency: str = "daily"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

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

    def filter_tasks(
        self,
        owner: Owner,
        pet_name: str | None = None,
        completed: bool | None = None,
        as_of: date | None = None,
    ) -> list[tuple[Pet, Task]]:
        """Filter tasks by pet name, completion state, and due date."""
        target_date = as_of or date.today()
        return [
            (pet, task)
            for pet, task in owner.get_all_tasks()
            if (pet_name is None or pet.name.casefold() == pet_name.casefold())
            and (completed is None or task.completed is completed)
            and task.due_date <= target_date
        ]

    def get_tasks(
        self,
        owner: Owner,
        include_completed: bool = False,
        pet_name: str | None = None,
        as_of: date | None = None,
    ) -> list[tuple[Pet, Task]]:
        """Collect due tasks, excluding completed tasks unless requested."""
        completed = None if include_completed else False
        return self.filter_tasks(owner, pet_name=pet_name, completed=completed, as_of=as_of)

    def sort_by_time(self, tasks: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Sort pet-task pairs by HH:MM time, then pet and task name."""
        return sorted(
            tasks,
            key=lambda item: (
                self._time_sort_key(item[1].time),
                item[0].name.casefold(),
                item[1].description.casefold(),
            ),
        )

    def get_schedule(self, owner: Owner, include_completed: bool = False) -> list[tuple[Pet, Task]]:
        """Sort tasks by their scheduled time, then pet and description."""
        """Return due tasks in time order, optionally including completed tasks."""
        return self.sort_by_time(self.get_tasks(owner, include_completed))

    def detect_conflicts(self, tasks: list[tuple[Pet, Task]]) -> list[str]:
        """Return warnings for tasks that have an identical scheduled time."""
        by_time: dict[str, list[tuple[Pet, Task]]] = {}
        for pet, task in tasks:
            by_time.setdefault(task.time, []).append((pet, task))

        warnings = []
        for scheduled_time, collisions in sorted(by_time.items()):
            if len(collisions) > 1:
                details = "; ".join(
                    f"{pet.name} - {task.description}" for pet, task in collisions
                )
                warnings.append(f"Warning: conflict at {scheduled_time}: {details}.")
        return warnings

    def mark_task_complete(
        self,
        pet: Pet,
        task: Task,
        completed_on: date | None = None,
    ) -> Task | None:
        """Complete a task and add its next daily or weekly occurrence, if any."""
        if task not in pet.tasks or task.completed:
            return None

        task.mark_complete()
        recurrence_days = {"daily": 1, "weekly": 7}
        days = recurrence_days.get(task.frequency.casefold())
        if days is None:
            return None

        next_due_date = (completed_on or date.today()) + timedelta(days=days)
        next_task = Task(
            description=task.description,
            time=task.time,
            frequency=task.frequency,
            due_date=next_due_date,
        )
        pet.add_task(next_task)
        return next_task

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
