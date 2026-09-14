FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

# RATE_LIMIT_ENABLED defaults to false; override at deploy time via
# k8s/deployment.yaml env var to run the "after" security test.
ENV RATE_LIMIT_ENABLED=false

CMD ["python", "app.py"]
