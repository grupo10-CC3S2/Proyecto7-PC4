from flask import Flask, Response
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

app = Flask(__name__)

LIMA_TZ = ZoneInfo("America/Lima")


@app.route("/")
def get_current_time():
    now = datetime.now(timezone.utc)
    now_lima = now.astimezone(LIMA_TZ)

    response_string = now.strftime("La hora es %I:%M %p, UTC.\n")
    response_string += now_lima.strftime("La hora en Lima es %I:%M %p.\n")
    return Response(response_string, mimetype='text/plain')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)