from app.agent_state import AgentState

state = AgentState(
    current_task="Create two tasks",
    status="running",
)

print(state)

state.iteration += 1

state.messages.append(
    {
        "role": "user",
        "content": "Create two tasks",
    }
)

print("\nUpdated state:")
print(state)

print("\nStatus:", state.status)
print("Iteration:", state.iteration)
