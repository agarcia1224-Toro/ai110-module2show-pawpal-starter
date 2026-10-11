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
else:
    st.info("Add a pet to start building a care schedule.")

st.header("Care tasks")
if owner.pets:
    with st.form("add_task_form", clear_on_submit=True):
        selected_pet = st.selectbox(
            "Pet",
            options=owner.pets,
            format_func=lambda pet: pet.name,
        )
        description = st.text_input("Task description", placeholder="Morning walk")
        task_time = st.time_input("Scheduled time", value=time(8, 0))
        frequency = st.selectbox("Frequency", ["daily", "weekly", "as needed"])
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        if not description.strip():
            st.error("Enter a description for the task.")
        else:
            selected_pet.add_task(
                Task(
                    description=description.strip(),
                    time=task_time.strftime("%H:%M"),
                    frequency=frequency,
                )
            )
            st.success(f"Added {description.strip()} for {selected_pet.name}.")
else:
    st.caption("Add a pet before creating care tasks.")

st.header("Today's schedule")
schedule = scheduler.get_schedule(owner)
if schedule:
    for warning in scheduler.detect_conflicts(schedule):
        st.warning(warning)

    task_positions = {
        id(task): (pet_index, task_index)
        for pet_index, pet in enumerate(owner.pets)
        for task_index, task in enumerate(pet.tasks)
    }
    for pet, task in schedule:
        pet_index, task_index = task_positions[id(task)]
        st.write(f"**{task.time}** · {pet.name} · {task.description} ({task.frequency})")
        if st.button("Mark complete", key=f"complete_{pet_index}_{task_index}"):
            scheduler.mark_task_complete(pet, task)
            st.rerun()
else:
    st.info("No incomplete tasks scheduled. Add a care task above.")

completed_tasks = [
    (pet, task)
    for pet, task in owner.get_all_tasks()
    if task.completed
]
if completed_tasks:
    with st.expander(f"Completed tasks ({len(completed_tasks)})"):
        for pet, task in completed_tasks:
            st.write(f"✓ {task.time} · {pet.name} · {task.description}")
