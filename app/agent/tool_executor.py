from typing import Any

from app.agent_state import AgentState
from app.state_storage import save_state
from app.tools.task_tools import create_task, get_tasks, delete_task


class ToolExecutor:

    def execute_tool(self, tool_name: str, arguments: dict):
        if tool_name == "create_task":
            return create_task(**arguments)

        elif tool_name == "get_tasks":
            return get_tasks()

        elif tool_name == "delete_task":
            return delete_task(**arguments)

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def execute_idempotently(
        self,
        state: AgentState,
        tool_call_id: str,
        tool_name: str,
        arguments: dict,
    ) -> Any:
        for tool_result in state.tool_results:
            if tool_result["tool_call_id"] == tool_call_id:
                print(f"[IDEMPOTENCY] Reusing result: {tool_call_id}")
                return tool_result["result"]

        print(f"[IDEMPOTENCY] Executing tool: {tool_call_id}")

        result = self.execute_tool(tool_name, arguments)

        state.tool_results.append(
            {
                "tool_call_id": tool_call_id,
                "tool_name": tool_name,
                "result": result,
            }
        )

        save_state(state)

        return result

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                            },
                        },
                        "required": ["title", "priority"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_tasks",
                    "description": "Get all tasks",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task by its ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to delete",
                            },
                        },
                        "required": ["task_id"],
                    },
                },
            },
        ]

    def requires_approval(self, tool_name: str) -> bool:
        dangerous_tools = {
            "delete_task",
        }

        return tool_name in dangerous_tools
