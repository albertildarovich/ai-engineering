from app.state_storage import load_state


def is_tool_executed(state, tool_call_id: str) -> bool:
    for tool_result in state.tool_results:
        if tool_result["tool_call_id"] == tool_call_id:
            return True

    return False


def get_tool_result(state, tool_call_id: str):
    for tool_result in state.tool_results:
        if tool_result["tool_call_id"] == tool_call_id:
            return tool_result["result"]

    return None


def get_saved_tool_result(state, tool_call_id: str):
    for tool_result in state.tool_results:
        if tool_result["tool_call_id"] == tool_call_id:
            return tool_result["result"]

    return None


def recover_agent():
    state = load_state()

    if state is None:
        print("No saved state found.")
        return None

    if state.status == "completed":
        print("Agent has already completed its task.")
        return None

    if state.status == "failed":
        print("Agent failed. Recovery may be needed.")

    if state.status == "running":
        print("Agent was interrupted. Ready to resume.")

    return state


if __name__ == "__main__":
    recover_agent()
