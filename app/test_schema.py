from app.schemas import Task


task = Task(
    title="Изучить FastAPI",
    priority="high",
    completed=False,
)

print(task)
print(task.model_dump())
