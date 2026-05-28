# GCP Deployment Guide

Deploy AI-Empower-Coding-Pilot to Google Cloud Platform using Terraform and Cloud Build.

## Architecture

```
                    ┌──────────────────────────────────┐
                    │   Global HTTPS Load Balancer      │
                    │   (Cloud Armor WAF + CDN)         │
                    └───────────┬──────────────────────┘
                                │
                   ┌────────────┴────────────┐
                   │                         │
              /api/*                      /* (static)
                   │                         │
         ┌────────▼────────┐       ┌────────▼────────┐
         │   Cloud Run     │       │   Cloud Run     │
         │   Backend       │       │   Frontend      │
         │   (FastAPI)     │       │   (Nginx+React) │
         └───┬──────┬──────┘       └─────────────────┘
             │      │
    ┌────────▼┐  ┌──▼──────────┐
    │Cloud SQL│  │ Memorystore │
    │PostgreSQL│ │   (Redis)   │
    └─────────┘  └─────────────┘
         │
    ┌────▼──────────────────────┐
    │  Secret Manager           │
    │  (API keys, JWT, DB creds)│
    └───────────────────────────┘
    ┌───────────────────────────┐
    │  Cloud Storage            │
    │  (data, logs, ChromaDB)   │
    └───────────────────────────┘
    ┌───────────────────────────┐
    │  Artifact Registry        │
    │  (Docker images)          │
    └───────────────────────────┘
    ┌───────────────────────────┐
    │  Cloud Monitoring         │
    │  (alerts, dashboard)      │
    └───────────────────────────┘
```

## GCP Services Used

| Service              | Purpose                                    |
|----------------------|--------------------------------------------|
| Cloud Run            | Backend (FastAPI) + Frontend (Nginx/React)  |
| Cloud SQL            | PostgreSQL 15 (replaces SQLite)             |
| Memorystore          | Redis 7.0 caching                          |
| Secret Manager       | API keys, JWT secrets, DB credentials      |
| Artifact Registry    | Docker image repository                    |
| Cloud Storage        | Application data, logs, ChromaDB vectors   |
| VPC + VPC Connector  | Private networking for Cloud Run           |
| Cloud Load Balancer  | Global HTTPS with path-based routing       |
| Cloud Armor          | WAF with rate limiting (100 req/min/IP)    |
| Cloud Build          | CI/CD pipeline                             |
| Cloud Monitoring     | Alerts + dashboard                         |
| Cloud NAT            | Outbound internet for private resources    |
| IAM                  | Least-privilege service accounts           |

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`)
- Docker (for local builds)
- A GCP project with billing enabled
- `Owner` or `Editor` role on the project

## Quick Start

### 1. Bootstrap the GCP Project

```bash
export GCP_PROJECT_ID=your-project-id
./infra/gcp/scripts/setup.sh dev
```

This enables APIs, creates the Terraform state bucket, and seeds Secret Manager entries.

### 2. Add Secrets

```bash
# OpenAI API key
echo -n 'sk-...' | gcloud secrets versions add ai-empower-openai-api-key-dev --data-file=-

# JWT secret (generate a random string)
openssl rand -base64 32 | gcloud secrets versions add ai-empower-jwt-secret-key-dev --data-file=-

# API secret
openssl rand -base64 32 | gcloud secrets versions add ai-empower-api-secret-key-dev --data-file=-
```

### 3. Deploy Infrastructure with Terraform

```bash
cd infra/gcp/environments/dev
terraform init
terraform plan -var project_id=$GCP_PROJECT_ID
terraform apply -var project_id=$GCP_PROJECT_ID
```

### 4. Build and Deploy Application

**Option A — Cloud Build (recommended):**

```bash
gcloud builds submit --config infra/gcp/cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=dev,_REGION=us-central1
```

**Option B — Local build + push:**

```bash
./infra/gcp/scripts/deploy.sh dev
```

## Environments

| Environment | DB Tier            | Redis     | Backend Instances | Notes                        |
|-------------|--------------------|-----------|-------------------|------------------------------|
| `dev`       | `db-f1-micro`      | BASIC 1GB | 0–3 (scale to 0)  | Cost-optimized               |
| `staging`   | `db-g1-small`      | BASIC 1GB | 1–5               | Pre-prod validation          |
| `prod`      | `db-custom-2-7680` | HA 2GB    | 2–20              | HA, backups, delete protect  |

### Deploy to a Specific Environment

```bash
cd infra/gcp/environments/<env>
terraform init
terraform plan -var project_id=$GCP_PROJECT_ID
terraform apply -var project_id=$GCP_PROJECT_ID
```

## CI/CD with Cloud Build

The `cloudbuild.yaml` pipeline:

1. **Lint & Test** — Runs `ruff` and `pytest` on the backend
2. **Type Check & Build** — Runs `tsc` and `vite build` on the frontend (in parallel)
3. **Build Docker Images** — Multi-stage builds for backend and frontend
4. **Push to Artifact Registry** — Tags with commit SHA and `latest`
5. **Deploy to Cloud Run** — Updates both services
6. **Verify Health** — Checks `/api/health` endpoint

### Setting Up Triggers

In Cloud Console → Cloud Build → Triggers:

| Trigger             | Event         | Branch/Tag      | `_ENVIRONMENT` |
|---------------------|---------------|-----------------|----------------|
| Deploy to dev       | Push          | `main`          | `dev`          |
| Deploy to staging   | Push tag      | `v*-staging`    | `staging`      |
| Deploy to prod      | Push tag      | `v*` (not staging) | `prod`      |

## Monitoring

The Terraform creates:

- **Alerts**: Backend latency (p99 > 5s), error rate (5xx > 5%), Cloud SQL CPU > 80%, Redis memory > 80%
- **Uptime check**: Backend `/api/health` every 5 minutes
- **Dashboard**: Request count, latency, DB CPU, Redis memory

Configure `notification_email` in your tfvars to receive alerts.

## Security

- **VPC-only networking**: Cloud SQL and Redis accessible only within the VPC
- **Secret Manager**: No secrets in environment variables or code
- **Cloud Armor**: Rate limiting at 100 requests/minute per IP
- **IAM least-privilege**: Separate service accounts for backend, frontend, and Cloud Build
- **Private Google Access**: Resources access Google APIs without public IPs
- **Encrypted at rest**: All data encrypted by default (Google-managed keys)

## Cost Estimate (Monthly)

| Component      | Dev       | Staging   | Prod        |
|----------------|-----------|-----------|-------------|
| Cloud Run      | ~$0–5     | ~$15–30   | ~$50–200    |
| Cloud SQL      | ~$10      | ~$25      | ~$100–200   |
| Memorystore    | ~$35      | ~$35      | ~$100       |
| Load Balancer  | ~$18      | ~$18      | ~$18        |
| Storage        | ~$1       | ~$1       | ~$5–20      |
| **Total**      | **~$65**  | **~$95**  | **~$275+**  |

> Dev uses scale-to-zero Cloud Run to minimize costs. Costs vary with traffic.

## Teardown

```bash
export GCP_PROJECT_ID=your-project-id
./infra/gcp/scripts/teardown.sh dev
```

> **Warning**: Production has `deletion_protection` enabled on Cloud SQL. Disable it manually before destroying.

## File Structure

```
infra/gcp/
├── main.tf                          # Root module (composes all sub-modules)
├── variables.tf                     # Input variables
├── outputs.tf                       # Output values
├── terraform.tfvars.example         # Example configuration
├── cloudbuild.yaml                  # CI/CD pipeline
├── modules/
│   ├── networking/                  # VPC, subnets, NAT, firewall, VPC connector
│   ├── iam/                         # Service accounts + role bindings
│   ├── artifact-registry/           # Docker image repository
│   ├── cloud-sql/                   # PostgreSQL instance
│   ├── redis/                       # Memorystore Redis
│   ├── storage/                     # GCS buckets (data, logs, ChromaDB)
│   ├── secrets/                     # Secret Manager
│   ├── cloud-run/                   # Backend + Frontend services
│   ├── load-balancer/               # Global HTTPS LB + Cloud Armor
│   └── monitoring/                  # Alerts + dashboard
├── environments/
│   ├── dev/                         # Dev env with remote state
│   ├── staging/                     # Staging env
│   └── prod/                        # Prod env (HA, deletion protection)
└── scripts/
    ├── setup.sh                     # One-time project bootstrap
    ├── deploy.sh                    # Quick local build + deploy
    └── teardown.sh                  # Destroy environment
```
