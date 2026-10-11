"""Run a small terminal demonstration of the PawPal+ scheduler."""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    """Create sample pets and print their daily schedule."""
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog", "Shiba Inu", 3)
    luna = Pet("Luna", "cat", "Tabby", 5)
    mochi.add_task(Task("Morning walk", "08:00", "daily"))
    mochi.add_task(Task("Breakfast", "08:30", "daily"))
    luna.add_task(Task("Medication", "09:00", "daily"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    print(Scheduler().format_schedule(owner))


if __name__ == "__main__":
    main()
