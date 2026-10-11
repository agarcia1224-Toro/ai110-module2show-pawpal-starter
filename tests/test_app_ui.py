"""Streamlit UI regression tests for owner and task persistence."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_added_task_is_saved_to_owner_and_shown_in_schedule() -> None:
    """Submitting the task form updates the stored pet and schedule table."""
    app_file = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_file)).run(timeout=10)

    app.text_input[1].set_value("Mochi")
    app.button[0].click().run(timeout=10)
    next(field for field in app.text_input if field.label == "Task description").set_value(
        "Morning walk"
    )
    next(button for button in app.button if button.label == "Add task").click().run(timeout=10)

    assert not app.exception
    owner = app.session_state["owner"]
    assert len(owner.pets) == 1
    assert [task.description for task in owner.pets[0].tasks] == ["Morning walk"]
    assert any(tab.label == "Mochi" for tab in app.tabs)
    assert "Morning walk" in app.table[0].value["Care task"].values
