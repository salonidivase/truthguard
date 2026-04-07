FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for frontend build
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Copy backend
COPY backend/ ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy frontend and build
COPY frontend/ ./frontend/
WORKDIR /app/frontend
RUN npm install && npm run build

WORKDIR /app

# Create __init__ files
RUN touch backend/env/__init__.py backend/tasks/__init__.py \
    backend/agents/__init__.py backend/grader/__init__.py

EXPOSE 7860


CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
EXPOSE 7860

CMD ["python", "backend/main.py"]
