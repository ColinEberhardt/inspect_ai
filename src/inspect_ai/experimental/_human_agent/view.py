from typing import Protocol


class HumanAgentView(Protocol):
    def set_status(self, status: str) -> None: ...
    def set_time(self, time: float) -> None: ...
