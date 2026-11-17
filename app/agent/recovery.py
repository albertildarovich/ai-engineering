import json

from app.agent_state import AgentState, PendingApproval
from app.agent.tool_executor import ToolExecutor
from app.state_storage import save_state


class Recovery:

    def __init__(self, tool_executor: ToolExecutor):
        self.tool_executor = tool_executor

    def process_pending_tool_calls(self, state: AgentState):
        if state.status == "waiting_for_approval":
            print("[RECOVERY] Waiting for human approval. Skipping.")
            return
        
        if not state.messages:
            return

        assistant_message = None

        for message in reversed(state.messages):
            if message.get("role") == "assistant" and message.get("tool_calls"):
                assistant_message = message
                break

        if assistant_message is None:
            return

        tool_calls = assistant_message["tool_calls"]

        completed_tool_ids = {
            message["tool_call_id"]
            for message in state.messages
            if message.get("role") == "tool" and message.get("tool_call_id")
        }

        for tool_call in tool_calls:
            tool_call_id = tool_call["id"]

            if tool_call_id in completed_tool_ids:
                print(f"[RECOVERY] Already completed: {tool_call_id}")
                continue

            function = tool_call["function"]

            tool_name = function["name"]
            arguments = function["arguments"]

            if self.tool_executor.requires_approval(tool_name):
                state.pending_approval = PendingApproval(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    arguments=arguments,
                )

                state.status = "waiting_for_approval"
                save_state(state)

                print(f"[RECOVERY] Approval required: {tool_name}")
                return

            print(f"[RECOVERY] Executing missing tool: {tool_name}")

            result = self.tool_executor.execute_idempotently(
                state,
                tool_call_id,
                tool_name,
                arguments,
            )

            state.messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "tool_name": tool_name,
                    "tool_call_id": tool_call_id,
                }
            )

            completed_tool_ids.add(tool_call_id)

            save_state(state)
