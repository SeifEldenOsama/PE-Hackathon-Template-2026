FROM python:3.12-slim
RUN apt-get update && apt-get install -y libpq-dev gcc curl && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"
WORKDIR /app
COPY . /app/
RUN uv venv && uv sync
EXPOSE 5000
CMD ["uv", "run", "run.py"]
