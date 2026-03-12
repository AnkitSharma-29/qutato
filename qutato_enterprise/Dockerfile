# Professional Production Build for Qutato Gateway
FROM python:3.11-slim

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY qutato_enterprise/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire workspace (needed for core engines)
# In production, you might want to install qutato_core as a package
COPY . .

# Set PYTHONPATH to include the workspace root
ENV PYTHONPATH=/app

# Expose the gateway port
EXPOSE 8000

# Start the gateway with uvicorn
CMD ["uvicorn", "qutato_enterprise.gateway.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
