FROM python:3.12
ENV PYTHONUNBUFFERED 1
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD python3 server.py