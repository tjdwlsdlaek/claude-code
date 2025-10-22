FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy common modules
COPY common/ /app/common/
COPY requirements.txt /app/requirements.txt

# Copy Strands specific files
COPY strands_agent/ /app/strands_agent/

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir -r /app/strands_agent/requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8002/health')"

# Run the application
CMD ["python", "-m", "uvicorn", "strands_agent.app:app", "--host", "0.0.0.0", "--port", "8002"]
