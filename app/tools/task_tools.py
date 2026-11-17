tasks = []


def create_task(title: str, priority: str):
    task = {
        "id": len(tasks) + 1,
        "title": title,
        "priority": priority,
        "completed": False,
    }

    tasks.append(task)

    return task


def get_tasks():
    return tasks


def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return {
                "success": True,
                "message": f"Task {task_id} deleted",
            }

    return {
        "success": False,
        "message": f"Task {task_id} not found",
    }
