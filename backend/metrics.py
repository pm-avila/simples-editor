from collections import defaultdict
from threading import Lock


HISTOGRAM_BUCKETS = (0.1, 0.5, 1, 2, 5, 10, 30)


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self._compile_samples = defaultdict(list)
            self._execution_samples = defaultdict(list)
            self._compile_errors = defaultdict(int)
            self._execution_totals = defaultdict(int)
            self._active_sandboxes = 0
            self._websocket_connections = 0

    def observe_compile(self, phase: str, duration_seconds: float) -> None:
        with self._lock:
            self._compile_samples[phase].append(duration_seconds)

    def increment_compile_error(self, phase: str) -> None:
        with self._lock:
            self._compile_errors[phase] += 1

    def websocket_connected(self) -> None:
        with self._lock:
            self._websocket_connections += 1

    def websocket_disconnected(self) -> None:
        with self._lock:
            if self._websocket_connections > 0:
                self._websocket_connections -= 1

    def execution_started(self) -> None:
        with self._lock:
            self._active_sandboxes += 1

    def execution_finished(self) -> None:
        with self._lock:
            if self._active_sandboxes > 0:
                self._active_sandboxes -= 1

    def observe_execution(self, outcome: str, duration_seconds: float) -> None:
        with self._lock:
            self._execution_samples[outcome].append(duration_seconds)
            self._execution_totals[outcome] += 1

    def _render_histogram(self, name: str, samples_by_label: dict[str, list[float]], label_name: str) -> list[str]:
        lines = [f"# TYPE {name} histogram"]
        for label_value in sorted(samples_by_label):
            samples = samples_by_label[label_value]
            total = 0.0
            for bucket in HISTOGRAM_BUCKETS:
                count = sum(1 for sample in samples if sample <= bucket)
                lines.append(
                    f'{name}_bucket{{{label_name}="{label_value}",le="{bucket}"}} {count}'
                )
            lines.append(
                f'{name}_bucket{{{label_name}="{label_value}",le="+Inf"}} {len(samples)}'
            )
            for sample in samples:
                total += sample
            lines.append(f'{name}_sum{{{label_name}="{label_value}"}} {total:.6f}')
            lines.append(f'{name}_count{{{label_name}="{label_value}"}} {len(samples)}')
        return lines

    def render(self) -> str:
        with self._lock:
            lines = []
            lines.extend(
                self._render_histogram(
                    "simples_compile_duration_seconds",
                    dict(self._compile_samples),
                    "phase",
                )
            )
            lines.append("# TYPE simples_compile_errors_total counter")
            for phase in sorted(self._compile_errors):
                lines.append(
                    f'simples_compile_errors_total{{phase="{phase}"}} {self._compile_errors[phase]}'
                )
            lines.extend(
                self._render_histogram(
                    "simples_execution_duration_seconds",
                    dict(self._execution_samples),
                    "outcome",
                )
            )
            lines.append("# TYPE simples_executions_total counter")
            for outcome in sorted(self._execution_totals):
                lines.append(
                    f'simples_executions_total{{outcome="{outcome}"}} {self._execution_totals[outcome]}'
                )
            lines.append("# TYPE simples_active_sandboxes gauge")
            lines.append(f"simples_active_sandboxes {self._active_sandboxes}")
            lines.append("# TYPE simples_websocket_connections gauge")
            lines.append(f"simples_websocket_connections {self._websocket_connections}")
            return "\n".join(lines) + "\n"


METRICS = MetricsRegistry()


def render_metrics() -> str:
    return METRICS.render()
