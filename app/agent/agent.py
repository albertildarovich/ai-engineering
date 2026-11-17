import json
from typing import Any

from app.agent.llm_client import LLMClient
from app.agent.tool_executor import ToolExecutor
from app.agent_state import AgentState, PendingApproval
from app.state_storage import save_state
from app.agent.recovery import Recovery

MAX_ITERATIONS = 5


class Agent:

    def __init__(
        self,
        llm_client: LLMClient,
        tool_executor: ToolExecutor,
        recovery: Recovery,
    ):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.recovery = recovery

    async def start(self, state: AgentState) -> str:
        if state.status != "idle":
            raise RuntimeError("Agent must be idle to start a new task")

        return await self._run_loop(state)

    async def resume(self, state: AgentState) -> str:
        if state.status not in ("running", "failed"):
            raise RuntimeError("Agent must be running or failed to resume")

        return await self._run_loop(state)

    async def _run_loop(self, state: AgentState) -> str:
        try:
            self.recovery.process_pending_tool_calls(state)

            if state.status == "waiting_for_approval":
                return "Waiting for human approval"

            state.status = "running"
            save_state(state)

            while state.iteration < MAX_ITERATIONS:
                state.iteration += 1

                print(f"\n--- Agent iteration {state.iteration} ---")

                message = await self.llm_client.chat(
                    state.messages,
                    tools=self.tool_executor.get_tool_definitions(),
                )

                state.messages.append(message)
                save_state(state)

                tool_calls = message.get("tool_calls", [])

                if not tool_calls:
                    state.status = "completed"
                    save_state(state)

                    return message.get("content", "")

                for tool_call in tool_calls:
                    function = tool_call["function"]

                    tool_name = function["name"]
                    arguments = function["arguments"]
                    tool_call_id = tool_call["id"]

                    if self.tool_executor.requires_approval(tool_name):
                        state.pending_approval = PendingApproval(
                            tool_call_id=tool_call_id,
                            tool_name=tool_name,
                            arguments=arguments,
                        )

                        state.status = "waiting_for_approval"
                        save_state(state)

                        print(f"[APPROVAL REQUIRED] Tool: {tool_name}")
                        return "Waiting for human approval"

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

                    save_state(state)

            raise RuntimeError("Agent exceeded maximum iterations")

        except Exception:
            state.status = "failed"
            save_state(state)
            raise

    def _get_pending_approval(self, state: AgentState) -> PendingApproval:
        if state.status != "waiting_for_approval":
            raise RuntimeError("Agent is not waiting for approval")

        if state.pending_approval is None:
            raise RuntimeError("Pending approval not found")

        return state.pending_approval

    async def approve(self, state: AgentState) -> str:
        pending = self._get_pending_approval(state)

        result = self.tool_executor.execute_idempotently(
            state,
            pending.tool_call_id,
            pending.tool_name,
            pending.arguments,
        )

        state.messages.append({
            "role": "tool",
            "content": json.dumps(result, ensure_ascii=False),
            "tool_name": pending.tool_name,
            "tool_call_id": pending.tool_call_id,
        })

        state.pending_approval = None
        state.status = "running"

        save_state(state)

        return await self._run_loop(state)

    async def reject(self, state: AgentState) -> str:
        pending = self._get_pending_approval(state)

        state.messages.append({
            "role": "tool",
            "content": json.dumps({
                "success": False,
                "message": "Action rejected by user",
            }),
            "tool_name": pending.tool_name,
            "tool_call_id": pending.tool_call_id,
        })

        state.pending_approval = None
        state.status = "running"

        save_state(state)

        return await self._run_loop(state)