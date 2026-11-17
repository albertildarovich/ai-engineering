
import json
from pathlib import Path

from app.agent_state import AgentState


DEFAULT_STATE_FILE = (
    Path(__file__).resolve().parent.parent / "agent_state.json"
)


def save_state(
    state: AgentState,
    file_path: Path = DEFAULT_STATE_FILE,
) -> None:
    data = state.model_dump()

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4,
        )


def load_state(
    file_path: Path = DEFAULT_STATE_FILE,
) -> AgentState | None:
    if not file_path.exists():
        return None

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return AgentState.model_validate(data)
