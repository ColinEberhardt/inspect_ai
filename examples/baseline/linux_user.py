import asyncio

from textual.app import ComposeResult
from textual.widgets import Link

from inspect_ai.solver import Generate, Solver, TaskState, solver
from inspect_ai.util import InputPanel, input_panel


@solver
def linux_user() -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        panel = await input_panel("User", LinuxUserPanel)
        await asyncio.sleep(1)
        panel.activate()
        await asyncio.sleep(20)

        return state

    return solve


class LinuxUserPanel(InputPanel):
    def compose(self) -> ComposeResult:
        yield Link(
            "Go to textualize.io",
            url="https://textualize.io",
            tooltip="Click me",
        )
