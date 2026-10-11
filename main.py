"""Run a small terminal demonstration of the PawPal+ scheduler."""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    """Demonstrate sorting, filtering, recurrence, and conflict warnings."""
    scheduler = Scheduler()
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog", "Shiba Inu", 3)
    luna = Pet("Luna", "cat", "Tabby", 5)
    breakfast = Task("Breakfast", "07:30", "daily")
    mochi.add_task(Task("Morning walk", "08:00", "daily"))
    mochi.add_task(breakfast)
    luna.add_task(Task("Medication", "08:00", "weekly"))
    luna.add_task(Task("Refresh water", "18:00", "as needed"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    print(scheduler.format_schedule(owner))

    print("\nConflict warnings:")
    warnings = scheduler.detect_conflicts(scheduler.get_schedule(owner))
    if warnings:
        for warning in warnings:
            print(warning)
    else:
        print("  No conflicts found.")

    print("\nLuna's tasks:")
    for pet, task in scheduler.filter_tasks(owner, pet_name="Luna", completed=False):
        print(f"  {task.time} | {pet.name}: {task.description}")

    next_breakfast = scheduler.mark_task_complete(mochi, breakfast)
    if next_breakfast:
        print(
            f"\nRecurring task: {next_breakfast.description} is next due "
            f"{next_breakfast.due_date.isoformat()} at {next_breakfast.time}."
        )


if __name__ == "__main__":
    main()
