#!/bin/bash
set -e

echo "=== ChronicleOps End-to-End Test ==="

API_URL="http://localhost:8000"

echo "1. Testing health endpoint..."
curl -s $API_URL/health | python3 -m json.tool

echo -e "\n2. Creating company blueprint..."
BLUEPRINT_RESPONSE=$(curl -s -X POST $API_URL/api/v1/config/blueprints \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test SaaS Company",
    "industry": "saas",
    "initial_conditions": {
      "cash": 5000000,
      "monthlyBurn": 200000,
      "headcount": 20,
      "revenue_monthly": 100000
    },
    "constraints": {
      "hiringVelocityMax": 5,
      "workingCapitalMin": 500000
    },
    "policies": {
      "spendLimitMonthly": 300000,
      "approvalThreshold": 100000,
      "riskAppetite": 0.5
    },
    "market_exposure": {}
  }')

echo $BLUEPRINT_RESPONSE | python3 -m json.tool
BLUEPRINT_ID=$(echo $BLUEPRINT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Blueprint ID: $BLUEPRINT_ID"

echo -e "\n3. Creating timeline..."
TIMELINE_RESPONSE=$(curl -s -X POST $API_URL/api/v1/config/timelines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Timeline",
    "start_date": "2020-01-01T00:00:00Z",
    "end_date": "2020-12-31T00:00:00Z",
    "events": []
  }')

echo $TIMELINE_RESPONSE | python3 -m json.tool
TIMELINE_ID=$(echo $TIMELINE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Timeline ID: $TIMELINE_ID"

echo -e "\n4. Creating agent config..."
AGENT_CONFIG_RESPONSE=$(curl -s -X POST $API_URL/api/v1/config/agent-configs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agents",
    "agents": [
      {
        "role": "ceo",
        "objectives": {"growth": 0.3, "profitability": 0.3, "resilience": 0.4},
        "permissions": ["modify_headcount", "modify_pricing", "allocate_budget"],
        "approval_threshold": 1000000,
        "risk_appetite": 0.5
      }
    ]
  }')

echo $AGENT_CONFIG_RESPONSE | python3 -m json.tool
AGENT_CONFIG_ID=$(echo $AGENT_CONFIG_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Agent Config ID: $AGENT_CONFIG_ID"

echo -e "\n5. Creating simulation run..."
RUN_RESPONSE=$(curl -s -X POST $API_URL/api/v1/simulation/runs \
  -H "Content-Type: application/json" \
  -d "{
    \"blueprint_id\": \"$BLUEPRINT_ID\",
    \"timeline_id\": \"$TIMELINE_ID\",
    \"agent_config_id\": \"$AGENT_CONFIG_ID\",
    \"seed\": 42
  }")

echo $RUN_RESPONSE | python3 -m json.tool
RUN_ID=$(echo $RUN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Run ID: $RUN_ID"

echo -e "\n6. Starting simulation..."
curl -s -X POST $API_URL/api/v1/simulation/runs/$RUN_ID/start | python3 -m json.tool

echo -e "\n7. Running 5 ticks..."
TICK_RESPONSE=$(curl -s -X POST $API_URL/api/v1/simulation/runs/$RUN_ID/tick \
  -H "Content-Type: application/json" \
  -d '{"ticks": 5}')

echo $TICK_RESPONSE | python3 -m json.tool

echo -e "\n8. Getting simulation state..."
curl -s $API_URL/api/v1/simulation/runs/$RUN_ID/state | python3 -m json.tool

echo -e "\n9. Getting audit trail..."
AUDIT_RESPONSE=$(curl -s $API_URL/api/v1/simulation/runs/$RUN_ID/audit)
echo $AUDIT_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(json.dumps({'entry_count': len(data.get('entries', [])), 'verified': data.get('verified', False)}, indent=2))"

echo -e "\n=== End-to-End Test Complete ==="
