FROM python:3

RUN mkdir /app
WORKDIR /app
RUN adduser appuser

RUN pip install feedparser requests

COPY app.py /app/app.py

RUN chown -R appuser:appuser /app

USER appuser

ENTRYPOINT [ "python", "app.py" ]