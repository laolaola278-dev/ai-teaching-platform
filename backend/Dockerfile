FROM python:3.10-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY backend/pyproject.toml /app/pyproject.toml
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential \
  && pip install --upgrade pip \
  && pip install poetry \
  && pip install 'fastapi[all]' 'uvicorn[standard]' 'sqlalchemy' 'asyncpg' 'alembic' 'pydantic' 'python-dotenv' 'httpx' \
  && rm -rf /root/.cache
COPY backend /app/backend
WORKDIR /app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
