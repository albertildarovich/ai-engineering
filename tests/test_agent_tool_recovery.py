from app.agent_state import AgentState
from app.agent_recovery import is_tool_executed
from app.agent_recovery import get_tool_result


state = AgentState(
    tool_results=[
        {
            "tool_call_id": "call_123",
            "tool_name": "create_task",
            "result": {"id": 1},
        }
    ]
)

print(is_tool_executed(state, "call_123"))
print(is_tool_executed(state, "call_456"))
print(get_tool_result(state, "call_123"))
print(get_tool_result(state, "call_456"))