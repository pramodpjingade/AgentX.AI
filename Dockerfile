# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system utilities needed for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production runtime image
FROM python:3.11-slim AS runner

WORKDIR /app

# Copy python packages compiled in stage 1
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "api.router:api_router", "--host", "0.0.0.0", "--port", "8000"]
