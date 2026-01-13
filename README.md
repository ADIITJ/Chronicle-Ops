# ChronicleOps

Time-locked multi-agent company simulation platform for modeling realistic business operations under constraints.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  Company Builder │ Org Designer │ Timeline │ Dashboard       │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   API Gateway     │
                    │  Auth │ RBAC      │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐
│ Config Service │  │ Simulation Svc  │  │  Agent Svc      │
│ Blueprints     │  │ Time-Lock       │  │ Orchestrator    │
│ Timelines      │  │ Deterministic   │  │ Policy Check    │
└────────────────┘  └─────────────────┘  └─────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   PostgreSQL      │
                    │   Audit Ledger    │
                    └───────────────────┘
```

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- GCP account (for deployment)

### Local Development

```bash
# Clone and setup
git clone <repo>
cd company-simulation

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# Frontend
cd ../frontend
npm install

# Start services
docker-compose up -d
cd backend && uvicorn api.gateway:app --reload
cd frontend && npm run dev
```

### GCP Deployment

```bash
export GCLOUD_PATH=/Users/ashishdate/google-cloud-sdk/google-cloud-sdk/bin/gcloud
export PATH=$PATH:$(dirname $GCLOUD_PATH)

cd infra
terraform init
terraform plan
terraform apply

./scripts/deploy.sh
```

## Key Features

- **Time-Lock Enforcement**: Agents cannot access future events
- **Deterministic Execution**: Same seed → same outcomes
- **Audit Trail**: Tamper-evident ledger of all decisions
- **Policy Enforcement**: Guardrails prevent invalid actions
- **Counterfactual Analysis**: Regret scoring vs. alternatives
- **Multi-Tenant**: Isolated workspaces with RBAC

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
npm run build
```

## License

Proprietary
