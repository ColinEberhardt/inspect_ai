from inspect_ai.solver import Generate, Solver, TaskState, solver
from inspect_ai.util import inpu


@solver
def linux_user() -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        return state

    return solve
