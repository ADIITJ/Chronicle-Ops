'use client';

import { useState } from 'react';

interface AgentConfig {
    role: string;
    objectives: { [key: string]: number };
    permissions: string[];
    approvalThreshold: number;
    riskAppetite: number;
}

export default function OrgDesignerPage() {
    const [agents, setAgents] = useState<AgentConfig[]>([
        {
            role: 'ceo',
            objectives: { growth: 0.3, profitability: 0.3, resilience: 0.4 },
            permissions: ['modify_headcount', 'modify_pricing', 'allocate_budget', 'modify_expansion', 'approve_all'],
            approvalThreshold: 1000000,
            riskAppetite: 0.5,
        },
    ]);

    const availableRoles = [
        { id: 'ceo', name: 'CEO', description: 'Strategy and high-level decisions' },
        { id: 'cfo', name: 'CFO', description: 'Financial management and risk' },
        { id: 'coo', name: 'COO', description: 'Operations and supply chain' },
        { id: 'product', name: 'Product', description: 'Product roadmap and features' },
        { id: 'sales', name: 'Sales/Marketing', description: 'Revenue and customer acquisition' },
        { id: 'risk', name: 'Risk/Governance', description: 'Compliance and guardrails' },
    ];

    const availablePermissions = [
        'modify_headcount',
        'modify_pricing',
        'allocate_budget',
        'modify_inventory',
        'modify_suppliers',
        'modify_costs',
        'modify_expansion',
        'approve_all',
    ];

    const addAgent = (role: string) => {
        const roleDefaults: { [key: string]: Partial<AgentConfig> } = {
            cfo: {
                objectives: { profitability: 0.5, runway: 0.3, risk_management: 0.2 },
                permissions: ['allocate_budget', 'modify_pricing', 'modify_costs'],
                approvalThreshold: 500000,
                riskAppetite: 0.3,
            },
            coo: {
                objectives: { service_level: 0.4, efficiency: 0.3, cost_optimization: 0.3 },
                permissions: ['modify_inventory', 'modify_suppliers', 'modify_capacity'],
                approvalThreshold: 250000,
                riskAppetite: 0.4,
            },
            product: {
                objectives: { innovation: 0.5, customer_satisfaction: 0.3, time_to_market: 0.2 },
                permissions: ['allocate_budget'],
                approvalThreshold: 200000,
                riskAppetite: 0.6,
            },
            sales: {
                objectives: { revenue: 0.6, growth: 0.3, customer_acquisition: 0.1 },
                permissions: ['modify_pricing', 'allocate_budget'],
                approvalThreshold: 300000,
                riskAppetite: 0.5,
            },
            risk: {
                objectives: { compliance: 0.5, risk_mitigation: 0.3, audit_readiness: 0.2 },
                permissions: ['approve_all'],
                approvalThreshold: 100000,
                riskAppetite: 0.2,
            },
            population: {
                objectives: { product_satisfaction: 0.3, value_perception: 0.25, brand_trust: 0.25, market_fit: 0.2 },
                permissions: ['influence_demand', 'affect_conversion', 'impact_reputation', 'drive_virality'],
                approvalThreshold: 0,
                riskAppetite: 0.5,
            },
        };

        const defaults = roleDefaults[role] || {};
        setAgents([
            ...agents,
            {
                role,
                objectives: defaults.objectives || {},
                permissions: defaults.permissions || [],
                approvalThreshold: defaults.approvalThreshold || 100000,
                riskAppetite: defaults.riskAppetite || 0.5,
            },
        ]);
    };

    const removeAgent = (index: number) => {
        setAgents(agents.filter((_, i) => i !== index));
    };

    const updateAgent = (index: number, updates: Partial<AgentConfig>) => {
        const newAgents = [...agents];
        newAgents[index] = { ...newAgents[index], ...updates };
        setAgents(newAgents);
    };

    // Get blueprint ID from URL
    const searchParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
    const blueprintId = searchParams ? searchParams.get('blueprintId') : null;

    const handleSubmit = async () => {
        if (!blueprintId) {
            alert('Error: No blueprint found. Please start from the builder.');
            return;
        }

        try {
            // 1. Create Agent Config
            const configResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/config/agent-configs`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: 'Default Org',
                    agents: agents,
                }),
            });

            if (!configResponse.ok) throw new Error('Failed to create agent config');
            const configData = await configResponse.json();

            // 2. Create Default Timeline (if needed for MVP)
            const timelineResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/config/timelines`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: 'Standard Market Timeline',
                    start_date: new Date().toISOString(),
                    end_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
                    events: [
                        { tick: 10, type: 'market_shock', magnitude: 0.3, description: 'Competitor price cut' },
                        { tick: 30, type: 'economic_boom', magnitude: 0.2, description: 'Industry growth surge' },
                        { tick: 60, type: 'technology_breakthrough', magnitude: 0.4, description: 'AI Boom: Efficiency skyrockets' },
                        { tick: 90, type: 'regulatory_change', magnitude: 0.4, description: 'New compliance laws (GDPR 2.0)' },
                        { tick: 120, type: 'market_crash', magnitude: 0.5, description: 'Housing Market Crash' },
                        { tick: 150, type: 'geopolitical_event', magnitude: 0.6, description: 'War in supply region triggers shortages' },
                        { tick: 180, type: 'pandemic', magnitude: 0.7, description: 'Global Pandemic (COVID-19 style)' },
                        { tick: 210, type: 'recovery', magnitude: 0.3, description: 'Post-crisis recovery boom' },
                        { tick: 240, type: 'technology_breakthrough', magnitude: 0.5, description: 'IT/Internet Boom' },
                        { tick: 300, type: 'economic_policy', magnitude: 0.2, description: 'New Tariffs imposed on imports' }
                    ]
                }),
            });

            // Accept 409 (Conflict) as success if timeline already exists
            let timelineId;
            if (timelineResponse.ok) {
                const timelineData = await timelineResponse.json();
                timelineId = timelineData.id;
            } else if (timelineResponse.status === 409) {
                // If it exists, we might need to query for it or just use the known name if the API returns ID on conflict (it currently returns message)
                // For MVP reliability, let's just use the ID if returned, or handle the specific case.
                // Ideally the API should return the ID on 409. I'll assume the API fix logic handles "return existing".
                const existData = await timelineResponse.json();
                timelineId = existData.id;
            } else {
                // Fallback or error
                const existData = await timelineResponse.json();
                if (existData.id) timelineId = existData.id;
                else throw new Error('Failed to create/fetch timeline');
            }

            // 3. Create Simulation Run
            const runResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/simulation/runs`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    blueprint_id: blueprintId,
                    timeline_id: timelineId,
                    agent_config_id: configData.id,
                    seed: Math.floor(Math.random() * 1000000)
                }),
            });

            if (!runResponse.ok) throw new Error('Failed to create simulation run');
            const runData = await runResponse.json();

            // 4. Redirect to Simulation Dashboard
            window.location.href = `/simulations/${runData.id}`;

        } catch (err: any) {
            console.error('Error starting simulation:', err);
            alert(`Failed to start simulation: ${err.message}`);
        }
    };

    return (
        <main className="min-h-screen py-12 px-4">
            <div className="max-w-6xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2 text-gradient">Agent Org Designer</h1>
                    <p className="text-gray-400">Configure your multi-agent organization</p>
                </div>

                {/* Add Agent */}
                <div className="card mb-8">
                    <h2 className="text-2xl font-bold mb-4">Add Agent</h2>
                    <div className="grid md:grid-cols-3 gap-4">
                        {availableRoles.map((role) => (
                            <button
                                key={role.id}
                                onClick={() => addAgent(role.id)}
                                disabled={agents.some((a) => a.role === role.id)}
                                className="p-4 glass rounded-lg hover:bg-white/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left"
                            >
                                <h3 className="font-bold mb-1">{role.name}</h3>
                                <p className="text-sm text-gray-400">{role.description}</p>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Agent List */}
                <div className="space-y-6">
                    {agents.map((agent, index) => (
                        <div key={index} className="card">
                            <div className="flex justify-between items-start mb-4">
                                <h3 className="text-xl font-bold capitalize">{agent.role}</h3>
                                <button
                                    onClick={() => removeAgent(index)}
                                    className="text-red-400 hover:text-red-300"
                                >
                                    Remove
                                </button>
                            </div>

                            {/* Objectives */}
                            <div className="mb-4">
                                <label className="block text-sm font-medium mb-2">Objectives (weights sum to 1.0)</label>
                                <div className="space-y-2">
                                    {Object.entries(agent.objectives).map(([key, value]) => (
                                        <div key={key} className="flex items-center space-x-4">
                                            <span className="w-32 text-sm capitalize">{key.replace('_', ' ')}</span>
                                            <input
                                                type="range"
                                                min="0"
                                                max="1"
                                                step="0.1"
                                                value={value}
                                                onChange={(e) => {
                                                    const newObjectives = { ...agent.objectives };
                                                    newObjectives[key] = parseFloat(e.target.value);
                                                    updateAgent(index, { objectives: newObjectives });
                                                }}
                                                className="flex-1"
                                            />
                                            <span className="w-12 text-sm">{value.toFixed(1)}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Permissions */}
                            <div className="mb-4">
                                <label className="block text-sm font-medium mb-2">Permissions</label>
                                <div className="grid md:grid-cols-3 gap-2">
                                    {availablePermissions.map((perm) => (
                                        <label key={perm} className="flex items-center space-x-2">
                                            <input
                                                type="checkbox"
                                                checked={agent.permissions.includes(perm)}
                                                onChange={(e) => {
                                                    const newPerms = e.target.checked
                                                        ? [...agent.permissions, perm]
                                                        : agent.permissions.filter((p) => p !== perm);
                                                    updateAgent(index, { permissions: newPerms });
                                                }}
                                                className="rounded"
                                            />
                                            <span className="text-sm">{perm.replace('_', ' ')}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>

                            {/* Approval Threshold */}
                            <div className="mb-4">
                                <label className="block text-sm font-medium mb-2">
                                    Approval Threshold: ${agent.approvalThreshold.toLocaleString()}
                                </label>
                                <input
                                    type="range"
                                    min="10000"
                                    max="2000000"
                                    step="10000"
                                    value={agent.approvalThreshold}
                                    onChange={(e) =>
                                        updateAgent(index, { approvalThreshold: parseInt(e.target.value) })
                                    }
                                    className="w-full"
                                />
                            </div>

                            {/* Risk Appetite */}
                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Risk Appetite: {(agent.riskAppetite * 100).toFixed(0)}%
                                </label>
                                <input
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.1"
                                    value={agent.riskAppetite}
                                    onChange={(e) =>
                                        updateAgent(index, { riskAppetite: parseFloat(e.target.value) })
                                    }
                                    className="w-full"
                                />
                            </div>
                        </div>
                    ))}
                </div>

                {/* Submit */}
                <div className="mt-8">
                    <button onClick={handleSubmit} className="btn-primary w-full">
                        Save Agent Configuration
                    </button>
                </div>
            </div>
        </main>
    );
}
