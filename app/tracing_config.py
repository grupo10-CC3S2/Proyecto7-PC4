from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
import os


def setup_tracing(app):
    # recurso que aparecera en panel de Jaeger
    resource = Resource(attributes={
        "service.name": "timeserver-app"
    })

    # setea el proveedor de trazas con el recurso
    trace.set_tracer_provider(TracerProvider(resource=resource))

    jaeger_host = os.getenv("JAEGER_HOST", "jaeger-collector")
    jaeger_port = os.getenv("JAEGER_PORT", "4318")

    otlp_exporter = OTLPSpanExporter(
        endpoint=f"http://{jaeger_host}:{jaeger_port}/v1/traces"
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # config de métricas
    metric_reader = PeriodicExportingMetricReader(
        exporter=ConsoleMetricExporter(),
        export_interval_millis=5000,
    )
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))

    # clases de instrumentacion para facil setup de flask y logging
    FlaskInstrumentor().instrument_app(app)
    LoggingInstrumentor().instrument(set_logging_format=True)

    tracer = trace.get_tracer("timeservice.tracer")
    meter = metrics.get_meter("timeservice.meter")

    return tracer, meter