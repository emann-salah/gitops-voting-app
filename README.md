# GitOps Voting App

A three-tier voting app (Vue, Flask, PostgreSQL) with a complete delivery pipeline: **GitHub Actions** builds and publishes container images, and **ArgoCD** keeps a Kubernetes cluster in sync with Git.

A push to `main` is all it takes. Images are built, tagged with the commit SHA, the manifests are updated automatically, and ArgoCD rolls the change out. There is no manual `kubectl apply`.

## How it works

```mermaid
flowchart LR
    Dev([Developer]) -->|git push| Repo[(GitHub repo)]
    Repo --> CI[GitHub Actions]
    CI -->|push images, tag = commit SHA| GHCR[(GHCR)]
    CI -->|commit new image tags| Repo
    Argo[ArgoCD<br/>inside the cluster] -->|pulls manifests| Repo
    Argo -->|sync| K8s[Kubernetes<br/>web, api, postgres]
    K8s -->|pulls images| GHCR
```

1. **CI** validates the config, builds the `api` and `web` images, and pushes them to GHCR.
2. A final CI job writes the new image tag into `k8s/` and commits it back to `main`.
3. **ArgoCD** detects the change in Git and applies it to the cluster with a rolling update.

Git is the single source of truth. Delivery is pull-based, so the CI never needs access to the cluster.

## CI pipeline

`.github/workflows/ci.yml` runs on every push and pull request to `main`.

| Job | Purpose |
|---|---|
| `validate` | Validates `docker-compose.yml` and the YAML in `k8s/` |
| `build-push` | Builds `api` and `web` with a matrix build. Pushes to GHCR only on `main`, tagged with `github.sha` |
| `update-manifests` | Updates the image tags in `k8s/*-deployment.yaml` and commits them back |

Highlights: matrix build, least-privilege `permissions` per job, unique SHA tags instead of `latest`, and no pipeline loop because commits pushed with `GITHUB_TOKEN` do not trigger workflows.

## GitOps with ArgoCD

`argocd/application.yaml` points ArgoCD at the `k8s/` folder on `main`, with automated sync:

- `prune`: resources removed from Git are removed from the cluster
- `selfHeal`: manual changes in the cluster are reverted to match Git

## Tech stack

Docker, Docker Compose, Kubernetes, GitHub Actions, GitHub Container Registry, ArgoCD

## Getting started

**Prerequisites:** Docker, `kubectl`, and a local Kubernetes cluster (Docker Desktop, kind or Minikube).

**1. Install ArgoCD**

```bash
kubectl create namespace argocd
kubectl apply -n argocd --server-side -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

**2. Deploy the application**

```bash
kubectl apply -f argocd/application.yaml
kubectl get applications -n argocd
```

Wait for `Synced` and `Healthy`.

**3. Open the app**

```bash
kubectl port-forward svc/web-service 8081:8080
```

Browse to http://localhost:8081.

To run it without Kubernetes: `docker compose up --build`.

## Credits

Sample app from [garden-io/web-app-example](https://github.com/garden-io/web-app-example).

