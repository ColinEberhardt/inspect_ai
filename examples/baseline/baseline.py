from linux_user import linux_user

from inspect_ai import Task, task


@task
def baseline() -> Task:
    return Task(solver=linux_user())
