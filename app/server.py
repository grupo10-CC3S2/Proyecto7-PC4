from flask import Flask, Response, jsonify, request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from logger_service import start_background_logging, logger
from tracing_config import setup_tracing
import logging
from opentelemetry import trace


app = Flask(__name__)

tracer, meter = setup_tracing(app)

request_counter = meter.create_counter(
    "time.requests",
    description="Numero de requests por endpoint",
)

LIMA_TZ = ZoneInfo("America/Lima")
logging.basicConfig(level=logging.INFO)
app_logger = logging.getLogger(__name__)


@app.route("/")
def get_current_time():
    with tracer.start_as_current_span("get_current_time_operation") as time_span:
        timezone_param = request.args.get("timezone", default="lima", type=str)

        with tracer.start_as_current_span("calculate_time"):
            now = datetime.now(timezone.utc)
            now_lima = now.astimezone(LIMA_TZ)

            time_span.set_attribute("request.timezone", timezone_param)
            time_span.set_attribute("time.utc", now.isoformat())
            time_span.set_attribute("time.lima", now_lima.isoformat())

        # para contar las GET requests
        request_counter.add(1, {"endpoint": "/", "timezone": timezone_param})

        with tracer.start_as_current_span("format_response"):
            response_string = now.strftime("La hora es %I:%M %p, UTC.\n")
            response_string += now_lima.strftime("La hora en Lima es %I:%M %p.\n")

            app_logger.info(f"Time request for timezone: {timezone_param}")

        return Response(response_string, mimetype='text/plain')


@app.route("/health")
def health_check():
    with tracer.start_as_current_span("health_check_operation") as health_span:
        request_counter.add(1, {"endpoint": "/health"})

        with tracer.start_as_current_span("verify_health"):
            status = "ok"
            health_span.set_attribute("health.status", status)
            app_logger.info("Health check performed")

        return jsonify({"status": status})



# Se agrega esta ruta para verificar trazas de error en Jaeger

@app.route("/error")
def trigger_error():
    with tracer.start_as_current_span("trigger_error_operation") as error_span:
        try:
            result = 1 / 0
        except Exception as e:
            app_logger.error(f"Se ha producido un error deliberado: {e}", exc_info=True)

            error_span.set_status(trace.Status(trace.StatusCode.ERROR, "division por cero?"))
            error_span.record_exception(e)

            response = jsonify({"status": "error", "message": "error interno!"})
            response.status_code = 500

            request_counter.add(1, {"endpoint": "/error", "status": "error"})

            return response

if __name__ == "__main__":
    start_background_logging()
    logger.info("Flask server starting on 0.0.0.0:80")
    app.run(host='0.0.0.0', port=80)
