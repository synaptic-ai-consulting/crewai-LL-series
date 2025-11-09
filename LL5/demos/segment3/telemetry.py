"""
OpenTelemetry bridge for LL5 Segment 3 demo.

Sets up OTLP exporters for traces + metrics and wires CrewAI task events
into histograms / counters so the Grafana dashboard can visualize latency
and throughput.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import os
from typing import Dict

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode

from crewai.events import crewai_event_bus
from crewai.events.base_event_listener import BaseEventListener
from crewai.events.types.task_events import (
    TaskCompletedEvent,
    TaskFailedEvent,
    TaskStartedEvent,
)


OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")


def _grpc_target_and_security(url: str) -> tuple[str, bool]:
    """Return (target, insecure) tuple compatible with OTLP gRPC exporters."""
    if url.startswith("http://"):
        return url.removeprefix("http://"), True
    if url.startswith("https://"):
        return url.removeprefix("https://"), False
    return url, not url.startswith("https://")

RESOURCE = Resource.create(
    {
        "service.name": os.getenv("OTEL_SERVICE_NAME", "ll5-demo-crew"),
        "deployment.environment": os.getenv("OTEL_ENVIRONMENT", "local"),
    }
)


def _init_trace_provider() -> trace.Tracer:
    target, insecure = _grpc_target_and_security(OTLP_ENDPOINT)
    provider = TracerProvider(resource=RESOURCE)
    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=target, insecure=insecure)
        )
    )
    trace.set_tracer_provider(provider)
    return trace.get_tracer("ll5.segment3")


def _init_meter_provider() -> tuple[
    metrics.Meter,
    metrics.Counter,
    metrics.Counter,
    metrics.Histogram,
]:
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(
            endpoint=OTLP_ENDPOINT,
            insecure=OTLP_ENDPOINT.startswith("http://"),
        ),
        export_interval_millis=int(os.getenv("OTEL_EXPORT_INTERVAL_MS", "5000")),
    )
    meter_provider = MeterProvider(resource=RESOURCE, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    meter = metrics.get_meter("ll5.segment3")
    success_counter = meter.create_counter(
        "crew_tasks_success_total",
        description="Number of CrewAI tasks that completed successfully.",
    )
    failure_counter = meter.create_counter(
        "crew_tasks_failure_total",
        description="Number of CrewAI tasks that failed.",
    )
    latency_histogram = meter.create_histogram(
        "crew_tasks_latency_ms",
        unit="ms",
        description="Latency of CrewAI tasks.",
    )
    return meter, success_counter, failure_counter, latency_histogram


TRACER = _init_trace_provider()
METER, SUCCESS_COUNTER, FAILURE_COUNTER, LATENCY_HISTOGRAM = _init_meter_provider()


class CrewTelemetryBridge(BaseEventListener):
    """Registers CrewAI event listeners and forwards them to OpenTelemetry."""

    def __init__(self) -> None:
        self._task_start_times: Dict[str, datetime] = {}
        super().__init__()

    def setup_listeners(self, bus) -> None:  # type: ignore[override]
        @bus.on(TaskStartedEvent)
        def _on_task_started(_source, event: TaskStartedEvent) -> None:
            key = self._event_key(event)
            self._task_start_times[key] = event.timestamp

        @bus.on(TaskCompletedEvent)
        def _on_task_completed(_source, event: TaskCompletedEvent) -> None:
            task_name = event.task_name or (event.task.description if event.task else "task")
            attributes = {
                "crew.task.name": task_name,
                "crew.agent.role": event.agent_role or "unknown",
            }
            duration = self._pop_duration(event)

            LATENCY_HISTOGRAM.record(duration, attributes)
            print('DEBUG TELEMETRY span', attributes, duration)
            SUCCESS_COUNTER.add(1, attributes)

            with TRACER.start_as_current_span(
                name=f"task::{task_name}",
                attributes=attributes,
            ) as span:
                span.set_attribute("crew.task.duration_ms", duration)
                span.set_status(Status(status_code=StatusCode.OK))

        @bus.on(TaskFailedEvent)
        def _on_task_failed(_source, event: TaskFailedEvent) -> None:
            task_name = event.task_name or (event.task.description if event.task else "task")
            attributes = {
                "crew.task.name": task_name,
                "crew.agent.role": event.agent_role or "unknown",
            }
            duration = self._pop_duration(event)

            LATENCY_HISTOGRAM.record(duration, attributes)
            print('DEBUG TELEMETRY span', attributes, duration)
            FAILURE_COUNTER.add(1, attributes)

            with TRACER.start_as_current_span(
                name=f"task::{task_name}",
                attributes=attributes,
            ) as span:
                span.set_attribute("crew.task.duration_ms", duration)
                span.set_status(Status(StatusCode.ERROR, description=event.error))

    def _event_key(self, event: TaskStartedEvent | TaskCompletedEvent | TaskFailedEvent) -> str:
        if event.source_fingerprint:
            return event.source_fingerprint
        if event.task and getattr(event.task, "id", None):
            return str(event.task.id)
        return event.task_name or event.type

    def _pop_duration(
        self,
        event: TaskCompletedEvent | TaskFailedEvent,
    ) -> float:
        key = self._event_key(event)
        start = self._task_start_times.pop(key, event.timestamp)
        delta = event.timestamp - start
        return max(delta.total_seconds() * 1000, 0.0)


# Instantiate once so handlers register when this module is imported.
CREW_TELEMETRY_BRIDGE = CrewTelemetryBridge()



