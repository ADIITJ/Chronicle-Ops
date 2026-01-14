# Running ChronicleOps Simulation via Web UI

## Quick Start Guide

### 1. Start Infrastructure

```bash
# Start Docker containers (PostgreSQL + Redis)
docker-compose up -d

# Verify containers are running
docker-compose ps
```

### 2. Start Backend API

```bash
cd backend

# Run database migrations
DATABASE_URL="postgresql://chronicleops:dev_password_change_in_prod@localhost:5432/chronicleops" \
  alembic upgrade head

# Start API server
DATABASE_URL="postgresql://chronicleops:dev_password_change_in_prod@localhost:5432/chronicleops" \
  REDIS_HOST=localhost \
  OPENROUTER_API_KEY=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 \
  python3 -m uvicorn api.gateway:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: **http://localhost:8000**

### 3. Start Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Frontend will be available at: **http://localhost:3000**

---

## Using the Web UI

### Step 1: Create Company Blueprint

1. Navigate to **http://localhost:3000/builder**
2. Select an industry template (SaaS, D2C, or Manufacturing)
3. Configure initial conditions:
   - Initial cash
   - Monthly burn rate
   - Starting headcount
4. Set constraints:
   - Hiring velocity limits
   - Working capital minimums
5. Define policies:
   - Monthly spend limits
   - Approval thresholds
   - Risk appetite
6. Click **"Create Blueprint"**

### Step 2: Design Agent Organization

1. Navigate to **http://localhost:3000/org**
2. Add agents by clicking role cards:
   - CEO
   - CFO
   - COO
   - Product Manager
   - Sales/Marketing
   - Risk/Governance
3. For each agent, configure:
   - **Objectives**: Weight different goals (growth, profitability, resilience)
   - **Permissions**: Select allowed actions
   - **Approval Threshold**: Dollar amount requiring approval
   - **Risk Appetite**: 0-100% tolerance
4. Click **"Save Agent Configuration"**

### Step 3: Create Event Timeline

1. Navigate to **http://localhost:3000/timeline**
2. Set simulation period (start/end dates)
3. Select event packs:
   - Historical Events (2010-2026)
   - Macro Economic Events
   - Tech Disruptions
   - Regulatory Changes
   - Supply Chain Events
4. (Optional) Add custom events:
   - Click **"Add Event"**
   - Set event type, severity, duration
   - Define affected areas
   - Add parameter impacts
5. Click **"Save Timeline"**

### Step 4: Run Simulation

1. Navigate to **http://localhost:3000/simulations**
2. Click **"New Simulation"**
3. Select:
   - Company blueprint
   - Event timeline
   - Agent configuration
   - Random seed (for reproducibility)
4. Click **"Create Run"**
5. On the dashboard:
   - Click **"Start Simulation"** to begin
   - Use **"Step (1 tick)"** for single-step execution
   - Use **"Run (10 ticks)"** for batch execution
6. Monitor real-time metrics:
   - Cash position
   - Runway (months)
   - Monthly revenue
   - Monthly costs
   - Headcount
   - Service level

### Step 5: Review Pending Approvals

When agents propose actions exceeding their approval threshold:

1. Click **"Approvals"** button (shows count badge)
2. Review each pending action:
   - Action type
   - Parameters
   - Agent role
   - Reason
3. Click **"Approve"** to execute the action

### Step 6: Replay Simulation

1. Navigate to **http://localhost:3000/replay/[run-id]**
2. Use playback controls:
   - **Previous**: Go back one entry
   - **Play/Pause**: Auto-advance through entries
   - **Next**: Advance one entry
3. Review each audit entry:
   - Entry details (sequence, time, type, agent)
   - Action taken
   - State before/after
   - Policy check results

### Step 7: Compare Simulations

1. Navigate to **http://localhost:3000/compare**
2. Enter two run IDs
3. Click **"Compare"**
4. View side-by-side comparison:
   - Metrics table with differences
   - Percentage changes (color-coded)
   - Status comparison

---

## API Endpoints (for advanced users)

### Configuration
- `POST /api/v1/config/blueprints` - Create company blueprint
- `POST /api/v1/config/timelines` - Create event timeline
- `POST /api/v1/config/agent-configs` - Create agent configuration

### Simulation
- `POST /api/v1/simulation/runs` - Create simulation run
- `POST /api/v1/simulation/runs/{id}/start` - Start simulation
- `POST /api/v1/simulation/runs/{id}/tick` - Advance simulation
- `GET /api/v1/simulation/runs/{id}/state` - Get current state
- `GET /api/v1/simulation/runs/{id}/audit` - Get audit trail

### Agents
- `GET /api/v1/agents/runs/{id}/pending-approvals` - Get pending approvals
- `POST /api/v1/agents/runs/{id}/approve-action` - Approve action
- `POST /api/v1/agents/runs/{id}/trigger-decision-cycle` - Trigger agent decisions

### Policy
- `POST /api/v1/policy/evaluate-action` - Evaluate action against policies
- `POST /api/v1/policy/check-invariants` - Check state invariants
- `GET /api/v1/policy/policy-rules` - Get available policy rules

---

## Troubleshooting

### Backend not starting
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
pkill -f "uvicorn api.gateway:app"
```

### Frontend not starting
```bash
# Check if port 3000 is in use
lsof -i :3000

# Kill existing process
pkill -f "next dev"
```

### Database connection errors
```bash
# Verify PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Restart containers
docker-compose restart
```

### Missing dependencies
```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install
```

---

## Production Deployment

For GCP deployment, run:

```bash
./infra/scripts/deploy_gcp.sh
```

This will:
1. Create Cloud SQL instance
2. Set up Cloud Storage
3. Deploy backend to Cloud Run
4. Deploy frontend to Cloud Run
5. Configure CI/CD pipeline
