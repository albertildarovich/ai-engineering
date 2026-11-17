
import json
from pathlib import Path

from app.agent_state import AgentState


STATE_FILE = Path(__file__).resolve().parent.parent / "agent_state.json"


def save_state(state: AgentState) -> None:
    data = state.model_dump()

    with STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4,
        )


def load_state() -> AgentState | None:
    if not STATE_FILE.exists():
        return None

    with STATE_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return AgentState.model_validate(data)
