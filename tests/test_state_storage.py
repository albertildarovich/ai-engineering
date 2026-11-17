from app.agent_state import AgentState
from app.state_storage import save_state, load_state


def test_save_and_load_state(tmp_path):
    state_file = tmp_path / "test_state.json"

    original_state = AgentState(
        current_task="Test task",
        status="running",
        iteration=2,
    )

    save_state(original_state, state_file)

    loaded_state = load_state(state_file)

    assert loaded_state is not None
    assert loaded_state.current_task == "Test task"
    assert loaded_state.status == "running"
    assert loaded_state.iteration == 2


def test_load_state_when_file_does_not_exist(tmp_path):
    state_file = tmp_path / "missing.json"

    result = load_state(state_file)

    assert result is None
