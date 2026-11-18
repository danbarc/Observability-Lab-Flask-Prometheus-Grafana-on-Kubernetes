from flask import Flask, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
import random

app = Flask(__name__)

# Métricas customizadas
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'Latência das requisições',
    ['method', 'endpoint'],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]
)

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    if request.endpoint:
        duration = time.time() - request.start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.endpoint,
            status=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.endpoint
        ).observe(duration)
    return response

@app.route('/')
def index():
    # Simula um pouco de latência variável
    time.sleep(random.uniform(0.01, 0.15))
    return {'status': 'ok', 'message': 'Observability Lab Flask App'}

@app.route('/slow')
def slow():
    time.sleep(random.uniform(0.5, 1.5))
    return {'status': 'ok', 'message': 'slow endpoint'}

@app.route('/error')
def error():
    return {'status': 'error'}, 500

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)