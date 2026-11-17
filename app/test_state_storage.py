from app.state_storage import load_state

restored_state = load_state()

print("Restored state:")
print(restored_state.model_dump())

print("\nTask:")
print(restored_state.current_task)

print("\nIteration:")
print(restored_state.iteration)