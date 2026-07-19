# Task API — containerized service on Kubernetes with CI/CD

A small Flask REST API, containerized with Docker, deployed to Kubernetes, with a
GitHub Actions pipeline that tests, builds, and pushes the image automatically on
every merge to `main`. The application itself is intentionally simple — the point
of this project is demonstrating the delivery pipeline and infrastructure around it.

## What this demonstrates

- Writing a REST API with proper health checks for orchestration
- Containerizing an application following best practices (non-root user, slim base
  image, layer caching, healthcheck)
- Deploying to Kubernetes with resource limits, readiness/liveness probes, and
  horizontal autoscaling
- Separating configuration from code using ConfigMaps
- A CI/CD pipeline that runs tests, builds and pushes a versioned image, and
  validates Kubernetes manifests before merge

## Architecture

```
GitHub push --> GitHub Actions --> pytest --> Docker build --> push to GHCR
                                                              --> validate k8s manifests
                                                              (deploy step - see Next steps)
```

Kubernetes objects:
- `Deployment` — 2 replicas, resource requests/limits, readiness + liveness probes
- `Service` — ClusterIP exposing port 80 -> container port 5000
- `ConfigMap` — externalizes app configuration
- `HorizontalPodAutoscaler` — scales 2-6 replicas based on CPU utilization

## Running locally

```bash
cd app
pip install -r requirements.txt
python app.py
# API available at http://localhost:5000
```

Run tests:
```bash
cd app
pytest -v
```

## Running with Docker

```bash
cd app
docker build -t task-api:latest .
docker run -p 5000:5000 task-api:latest
```

## Deploying to Kubernetes

Requires a cluster (minikube, kind, or EKS) and `kubectl` configured against it.

```bash
# If using minikube, point Docker at the cluster's daemon first:
eval $(minikube docker-env)
docker build -t task-api:latest ./app

kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

kubectl get pods
kubectl port-forward svc/task-api-service 8080:80
# API available at http://localhost:8080
```

## API endpoints

| Method | Path          | Description         |
|--------|---------------|----------------------|
| GET    | `/health`     | Health check         |
| GET    | `/`           | Service info         |
| GET    | `/tasks`      | List tasks           |
| POST   | `/tasks`      | Create a task         |
| PATCH  | `/tasks/<id>` | Update a task         |
| DELETE | `/tasks/<id>` | Delete a task         |

## What I'd improve with more time

- Add a deploy step to the pipeline that applies manifests to a real cluster (currently
  the pipeline builds and validates but stops short of deploying — intentionally, to
  avoid requiring a live cluster credential for this demo repo)
- Replace the in-memory task store with a real database (Postgres via RDS) and add
  a migration step
- Add structured logging and ship it to CloudWatch or an ELK stack
- Add Prometheus metrics endpoint and a Grafana dashboard

## Tech stack

Python, Flask, Docker, Kubernetes, GitHub Actions, GitHub Container Registry
