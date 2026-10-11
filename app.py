"""Streamlit interface for the PawPal+ pet care scheduler."""

from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Streamlit reruns this file after each interaction. Keep the model instances in
# session_state so pets and tasks survive those reruns for the current session.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

st.title("🐾 PawPal+")
st.caption("Plan and keep track of your pets' daily care.")

owner.name = st.text_input("Owner name", value=owner.name)
completion_message = st.session_state.pop("completion_message", None)
if completion_message:
    st.success(completion_message)

st.header("Your pets")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed (optional)")
    age = st.number_input("Age in years (optional)", min_value=0, max_value=100, value=0)
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    if not pet_name.strip():
        st.error("Enter a name for your pet.")
    elif any(pet.name.casefold() == pet_name.strip().casefold() for pet in owner.pets):
        st.error("A pet with that name is already in your list. Choose a unique name.")
    else:
        owner.add_pet(
            Pet(
                name=pet_name.strip(),
                species=species,
                breed=breed.strip(),
                age=int(age) if age else None,
            )
        )
        st.success(f"Added {pet_name.strip()}.")

if owner.pets:
    st.write(" | ".join(f"**{pet.name}** ({pet.species})" for pet in owner.pets))

    st.subheader("Pet details and care schedules")
    pet_tabs = st.tabs([pet.name for pet in owner.pets])
    for pet, pet_tab in zip(owner.pets, pet_tabs):
        with pet_tab:
            details = [f"Species: {pet.species}"]
            if pet.breed:
                details.append(f"Breed: {pet.breed}")
            if pet.age is not None:
                details.append(f"Age: {pet.age} years")
            st.caption(" · ".join(details))

            pet_tasks = sorted(
                pet.tasks,
                key=lambda task: (task.due_date, task.time, task.description.casefold()),
            )
            if pet_tasks:
                st.table(
                    [
                        {
                            "Due date": task.due_date.isoformat(),
                            "Time": task.time,
                            "Care task": task.description,
                            "Frequency": task.frequency,
                            "Status": "Complete" if task.completed else "Incomplete",
                        }
                        for task in pet_tasks
                    ]
                )
            else:
                st.info(f"No care tasks have been added for {pet.name} yet.")
else:
    st.info("Add a pet to start building a care schedule.")

st.header("Care tasks")
if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        task_pet_name = st.selectbox(
            "Pet",
            options=[pet.name for pet in owner.pets],
        )
        description = st.text_input("Task description", placeholder="Morning walk")
        task_time = st.time_input("Scheduled time", value=time(8, 0))
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        if not description.strip():
            st.error("Enter a description for the task.")
        else:
            task_pet = next(pet for pet in owner.pets if pet.name == task_pet_name)
            task_pet.add_task(
                Task(
                    description=description.strip(),
                    time=task_time.strftime("%H:%M"),
                    frequency=frequency,
                )
            )
            st.success(f"Added {description.strip()} for {task_pet.name}.")
else:
    st.caption("Add a pet before creating care tasks.")

st.header("Today's schedule")
all_due_tasks = scheduler.get_schedule(owner)
for warning in scheduler.detect_conflicts(all_due_tasks):
    st.warning(f"{warning} Consider moving one of these tasks to another time.")

selected_pet_name = "All pets"
if owner.pets:
    selected_pet_name = st.selectbox(
        "Filter schedule by pet",
        options=["All pets", *(pet.name for pet in owner.pets)],
    )
    filtered_tasks = scheduler.filter_tasks(
        owner,
        pet_name=None if selected_pet_name == "All pets" else selected_pet_name,
        completed=False,
    )
    schedule = scheduler.sort_by_time(filtered_tasks)
else:
    schedule = []

if schedule:
    st.table(
        [
            {
                "Time": task.time,
                "Pet": pet.name,
                "Care task": task.description,
                "Frequency": task.frequency,
                "Due date": task.due_date.isoformat(),
            }
            for pet, task in schedule
        ]
    )

    task_positions = {
        id(task): (pet_index, task_index)
        for pet_index, pet in enumerate(owner.pets)
        for task_index, task in enumerate(pet.tasks)
    }
    st.caption(
        "Mark a task complete to close it; daily and weekly tasks get their next due date automatically."
    )
    for pet, task in schedule:
        pet_index, task_index = task_positions[id(task)]
        if st.button(
            f"Mark complete · {pet.name}: {task.description}",
            key=f"complete_{pet_index}_{task_index}",
        ):
            next_task = scheduler.mark_task_complete(pet, task)
            if next_task:
                st.session_state.completion_message = (
                    f"Completed {task.description}. Its next occurrence is due "
                    f"{next_task.due_date.isoformat()} at {next_task.time}."
                )
            else:
                st.session_state.completion_message = f"Marked {task.description} complete."
            st.rerun()
else:
    if owner.pets and selected_pet_name != "All pets":
        st.info(f"No incomplete tasks due for {selected_pet_name}.")
    else:
        st.info("No incomplete tasks scheduled. Add a care task above.")

completed_tasks = [
    (pet, task)
    for pet, task in owner.get_all_tasks()
    if task.completed
]
if completed_tasks:
    with st.expander(f"Completed tasks ({len(completed_tasks)})"):
        st.table(
            [
                {
                    "Time": task.time,
                    "Pet": pet.name,
                    "Care task": task.description,
                    "Frequency": task.frequency,
                }
                for pet, task in completed_tasks
            ]
        )
