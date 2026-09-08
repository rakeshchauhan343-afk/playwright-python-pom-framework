FROM mcr.microsoft.com/playwright/python:v1.52.0-noble

WORKDIR /tests
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .
ENTRYPOINT ["python", "-m", "pytest"]
