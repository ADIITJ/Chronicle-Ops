#!/bin/bash
set -e

API="http://localhost:8000/api/v1"

echo "🧪 Starting Full Pipeline Test..."

# 1. Create Blueprint
echo "-----------------------------------"
echo "1. Creating Blueprint..."
TIMESTAMP=$(date +%s)
BP_PAYLOAD=$(cat <<EOF
{
    "name": "Pipeline Test Corp $TIMESTAMP",
    "industry": "saas",
    "initial_conditions": {
        "cash": 1000000,
        "monthly_burn": 50000,
        "headcount": 10,
        "pricing": {"base": 100},
        "margins": {"gross": 0.7},
        "capacity": {}
    },
    "constraints": {
        "hiring_velocity_max": 5,
        "procurement_lead_time_days": {"raw_materials": [7, 14]},
        "working_capital_min": 100000,
        "compliance_strictness": 0.8
    },
    "policies": {
        "spend_limit_monthly": 50000,
        "approval_threshold": 10000,
        "max_percent_change": {"pricing": 0.2, "headcount": 0.3},
        "risk_appetite": 0.5
    },
    "market_exposure": {"volatility": 0.3, "seasonality": 0.1}
}
EOF
)

BP_RESP=$(curl -s -X POST "$API/config/blueprints" \
  -H "Content-Type: application/json" \
  -H "X-Idempotency-Key: bp-$TIMESTAMP" \
  -d "$BP_PAYLOAD")

echo "Response: $BP_RESP"
BP_ID=$(echo $BP_RESP | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✅ Blueprint ID: $BP_ID"

# 2. Create Agent Config
echo "-----------------------------------"
echo "2. Creating Agent Config..."
AG_PAYLOAD=$(cat <<EOF
{
    "name": "Pipeline Agents $TIMESTAMP",
    "agents": [
        {
            "role": "ceo",
            "objectives": {"growth": 0.5, "profit": 0.5},
            "permissions": ["approve_all"],
            "approvalThreshold": 1000000,
            "riskAppetite": 0.5
        }
    ]
}
EOF
)

AG_RESP=$(curl -s -X POST "$API/config/agent-configs" \
  -H "Content-Type: application/json" \
  -d "$AG_PAYLOAD")

echo "Response: $AG_RESP"
AG_ID=$(echo $AG_RESP | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✅ Agent Config ID: $AG_ID"

# 3. Create Timeline
echo "-----------------------------------"
echo "3. Creating Timeline..."
TL_PAYLOAD=$(cat <<EOF
{
    "name": "Pipeline Timeline $TIMESTAMP",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2025-01-01T00:00:00Z",
    "events": [
        {"tick": 10, "type": "market_shock", "magnitude": 0.3, "description": "Test Shock"}
    ]
}
EOF
)

TL_RESP=$(curl -s -X POST "$API/config/timelines" \
  -H "Content-Type: application/json" \
  -d "$TL_PAYLOAD")

echo "Response: $TL_RESP"
# Handle potential conflict if same name used (though we use unique timestamp)
TL_ID=$(echo $TL_RESP | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', data.get('message', '')))")
# If ID is not UUID-like, it might be an error or message
if [[ ! $TL_ID =~ ^[0-9a-f-]{36}$ ]]; then
    # Try fetching by name or just fail
    echo "⚠️  Creation might have failed or conflicted: $TL_ID"
else
    echo "✅ Timeline ID: $TL_ID"
fi

# 4. Create Run
echo "-----------------------------------"
echo "4. Creating Simulation Run..."
RUN_PAYLOAD=$(cat <<EOF
{
    "blueprint_id": "$BP_ID",
    "timeline_id": "$TL_ID",
    "agent_config_id": "$AG_ID",
    "seed": 12345
}
EOF
)

RUN_RESP=$(curl -s -X POST "$API/simulation/runs" \
  -H "Content-Type: application/json" \
  -d "$RUN_PAYLOAD")

echo "Response: $RUN_RESP"
RUN_ID=$(echo $RUN_RESP | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

if [[ $RUN_ID =~ ^[0-9a-f-]{36}$ ]]; then
    echo "✅ Run ID: $RUN_ID"
    echo "🎉 Test Passed!"
else
    echo "❌ Failed to create run"
    exit 1
fi
