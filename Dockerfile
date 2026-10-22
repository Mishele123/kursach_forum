FROM python:3.14-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/backend
WORKDIR /app
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
COPY backend ./backend
COPY alembic.ini ./
COPY migrations ./migrations
RUN mkdir -p /app/uploads
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --app-dir backend --host 0.0.0.0 --port 8000 --proxy-headers"]

FROM runtime AS test
COPY requirements-dev.txt ./
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements-dev.txt
COPY tests ./tests
CMD ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]
