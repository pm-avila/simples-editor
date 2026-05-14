import unittest

from backend.app import app
from backend.metrics import METRICS
from backend.metrics import render_metrics


class MetricsRenderTest(unittest.TestCase):
    def setUp(self):
        METRICS.reset()

    def test_renders_required_prometheus_metrics(self):
        METRICS.observe_compile("nasm", 0.25)
        METRICS.increment_compile_error("parser")
        METRICS.websocket_connected()
        METRICS.execution_started()
        METRICS.observe_execution("success", 0.5)
        METRICS.execution_finished()
        METRICS.websocket_disconnected()

        text = render_metrics()
        self.assertIn("# TYPE simples_compile_duration_seconds histogram", text)
        self.assertIn('phase="nasm"', text)
        self.assertIn("simples_compile_errors_total", text)
        self.assertIn('phase="parser"', text)
        self.assertIn("simples_execution_duration_seconds", text)
        self.assertIn('outcome="success"', text)
        self.assertIn("simples_executions_total", text)
        self.assertIn("simples_active_sandboxes", text)
        self.assertIn("simples_websocket_connections", text)

    def test_metrics_endpoint_returns_prometheus_text(self):
        METRICS.observe_compile("nasm", 0.25)
        METRICS.execution_started()

        app.config["TESTING"] = True
        client = app.test_client()
        response = client.get("/metrics")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response.content_type)
        body = response.get_data(as_text=True)
        self.assertIn("simples_compile_duration_seconds", body)
        self.assertIn("simples_active_sandboxes", body)


if __name__ == "__main__":
    unittest.main()
