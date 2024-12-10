from dataclasses import dataclass

from textual.app import ComposeResult
from textual.containers import Center, Grid
from textual.reactive import Reactive, reactive
from textual.widget import Widget
from textual.widgets import Static

from inspect_ai._display.core.display import TaskDisplayMetric


@dataclass
class TaskMetric:
    name: str
    value: float


class TaskDetail(Widget):
    hidden = reactive(False)
    DEFAULT_CSS = """
    TaskDetail {
        background: $surface-lighten-1;
        width: 100%;
        height: auto;
        padding: 1 0 1 0;
    }
    TaskDetail Grid {
        width: 100%;
        height: auto;
        grid-gutter: 1 3;
    }
    """

    def __init__(
        self,
        *,
        hidden: bool = True,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.hidden = hidden
        if self.hidden:
            self.add_class("hidden")
        self.existing_metrics: dict[str, TaskMetrics] = {}
        self.grid = Grid()
        self.by_reducer: dict[str | None, dict[str, list[TaskMetric]]] = {}
        self.metrics: list[TaskDisplayMetric] = []

    def watch_hidden(self, hidden: bool) -> None:
        """React to changes in the `visible` property."""
        if hidden:
            self.add_class("hidden")
        else:
            self.remove_class("hidden")

    def compose(self) -> ComposeResult:
        yield self.grid

    def on_mount(self) -> None:
        self.refresh_grid()

    def update_metrics(self, metrics: list[TaskDisplayMetric]) -> None:
        # Group by reducer then scorer within reducers
        self.metrics = metrics
        for metric in metrics:
            reducer_group = (
                self.by_reducer[metric.reducer]
                if metric.reducer in self.by_reducer
                else {}
            )

            by_scorer_metrics = (
                reducer_group[metric.scorer] if metric.scorer in reducer_group else []
            )
            by_scorer_metrics.append(TaskMetric(name=metric.name, value=metric.value))
            reducer_group[metric.scorer] = by_scorer_metrics
            self.by_reducer[metric.reducer] = reducer_group

        if self.grid.is_attached:
            self.refresh_grid()

    def refresh_grid(self) -> None:
        # Makes keys for tracking Task Metric widgets
        def metric_key(reducer: str | None, scorer: str) -> str:
            reducer = reducer or "none"
            return f"task-{reducer}-{scorer}-tbl"

        # Compute the row and column count
        row_count = len(self.by_reducer)
        col_count = len(next(iter(self.by_reducer.values())))

        # If this can fit in a single row, make it fit
        # otherwise place each reducer on their own row
        self.grid.styles.grid_columns = "auto"
        if row_count * col_count < 4:
            self.grid.styles.grid_size_columns = row_count * col_count
            self.grid.styles.grid_size_rows = 1
        else:
            self.grid.styles.grid_size_columns = col_count
            self.grid.styles.grid_size_rows = row_count

        # Remove keys that are no longer present
        existing_keys = set(self.existing_metrics.keys())
        new_keys = set(metric_key(m.reducer, m.scorer) for m in self.metrics)
        to_remove = existing_keys - new_keys
        for remove in to_remove:
            task_metric = self.existing_metrics[remove]
            task_metric.remove()

        # add or update widgets with metrics
        for reducer, scorers in self.by_reducer.items():
            for scorer, scores in scorers.items():
                key = metric_key(reducer=reducer, scorer=scorer)
                if key in self.existing_metrics:
                    task_metrics = self.existing_metrics[key]
                    task_metrics.update(scores)
                else:
                    task_metrics = TaskMetrics(
                        id=key, scorer=scorer, reducer=reducer, metrics=scores
                    )
                    self.grid.mount(task_metrics)
                    self.existing_metrics[key] = task_metrics


class TaskMetrics(Widget):
    DEFAULT_CSS = """
    TaskMetrics {
        width: auto;
        height: auto;
    }
    TaskMetrics Grid {
        width: auto;
        grid-size: 2;
        grid-columns: auto;
        grid-gutter: 0 3;
        padding: 0 2 0 2;
    }
    TaskMetric Center {
        width: auto;
    }
    TaskMetrics Center Static {
        width: auto;
    }
    """

    metrics: Reactive[list[TaskMetric]] = reactive([])

    def __init__(
        self,
        *,
        scorer: str | None,
        reducer: str | None,
        metrics: list[TaskMetric],
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(id=id, classes=classes)
        self.scorer = scorer
        self.reducer = reducer
        self.metrics = metrics
        self.grid: Grid = Grid()
        self.value_widgets: dict[str, Static] = {}

    def compose(self) -> ComposeResult:
        # Just yield a single DataTable widget
        yield Center(Static(self.title()))
        with Grid():
            for metric in self.metrics:
                yield Static(metric.name)
                self.value_widgets[metric.name] = Static(f"{metric.value:,.3f}")
                yield self.value_widgets[metric.name]

    def title(self) -> str:
        if self.scorer is None:
            return ""
        elif self.reducer is None:
            return self.scorer
        else:
            return f"{self.scorer}/{self.reducer}"

    def update(self, metrics: list[TaskMetric]) -> None:
        for metric in metrics:
            widget = self.value_widgets[metric.name]
            widget.update(content=f"{metric.value:,.3f}")
