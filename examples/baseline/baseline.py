from human import human

from inspect_ai import Task, task


@task
def baseline() -> Task:
    return Task(solver=human())
