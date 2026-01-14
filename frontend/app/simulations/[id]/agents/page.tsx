'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';

interface AgentDecision {
    id: string;
    tick: number;
    agent_role: string;
    observations: any;
    reasoning: string;
    proposed_actions: any[];
    approved: boolean;
    executed: boolean;
    created_at: string;
}

interface MarketState {
    tick: number;
    sentiment_score: number;
    awareness_level: number;
    trust_level: number;
    viral_coefficient: number;
    market_dynamics: any;
}

export default function AgentObservatoryPage() {
    const params = useParams();
    const runId = params.id as string;

    const [decisions, setDecisions] = useState<AgentDecision[]>([]);
    const [marketState, setMarketState] = useState<MarketState | null>(null);
    const [selectedAgent, setSelectedAgent] = useState<string>('all');
    const [autoRefresh, setAutoRefresh] = useState(true);

    useEffect(() => {
        fetchAgentData();

        if (autoRefresh) {
            const interval = setInterval(fetchAgentData, 2000);
            return () => clearInterval(interval);
        }
    }, [runId, selectedAgent, autoRefresh]);

    const fetchAgentData = async () => {
        try {
            // Fetch agent decisions
            const decisionsRes = await fetch(
                `/api/v1/simulation/runs/${runId}/agent-decisions?agent=${selectedAgent}`
            );
            if (decisionsRes.ok) {
                const data = await decisionsRes.json();
                setDecisions(data);
            }

            // Fetch market state
            const marketRes = await fetch(`/api/v1/simulation/runs/${runId}/market-state`);
            if (marketRes.ok) {
                const data = await marketRes.json();
                setMarketState(data);
            }
        } catch (error) {
            console.error('Failed to fetch agent data:', error);
        }
    };

    const agentRoles = ['all', 'ceo', 'cfo', 'coo', 'product', 'sales', 'risk', 'population'];

    return (
        <main className="min-h-screen py-8 px-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-4xl font-bold text-gradient">Agent Observatory</h1>
                        <p className="text-gray-400 mt-2">Real-time agent thinking and decision-making</p>
                    </div>
                    <div className="flex gap-4">
                        <button
                            onClick={() => setAutoRefresh(!autoRefresh)}
                            className={`px-4 py-2 rounded-lg ${autoRefresh ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                                }`}
                        >
                            {autoRefresh ? '● Live' : '○ Paused'}
                        </button>
                    </div>
                </div>

                {/* Market State Dashboard */}
                {marketState && (
                    <div className="card mb-8">
                        <h2 className="text-2xl font-bold mb-6">Market Dynamics</h2>
                        <div className="grid md:grid-cols-4 gap-6">
                            <div className="text-center">
                                <div className="text-4xl font-bold text-gradient mb-2">
                                    {(marketState.sentiment_score * 100).toFixed(0)}%
                                </div>
                                <div className="text-sm text-gray-400">Market Sentiment</div>
                                <div className="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"
                                        style={{ width: `${marketState.sentiment_score * 100}%` }}
                                    />
                                </div>
                            </div>

                            <div className="text-center">
                                <div className="text-4xl font-bold text-blue-400 mb-2">
                                    {(marketState.awareness_level * 100).toFixed(0)}%
                                </div>
                                <div className="text-sm text-gray-400">Brand Awareness</div>
                                <div className="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-blue-500"
                                        style={{ width: `${marketState.awareness_level * 100}%` }}
                                    />
                                </div>
                            </div>

                            <div className="text-center">
                                <div className="text-4xl font-bold text-purple-400 mb-2">
                                    {(marketState.trust_level * 100).toFixed(0)}%
                                </div>
                                <div className="text-sm text-gray-400">Consumer Trust</div>
                                <div className="mt-2 h-2 bg-gray-700 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-purple-500"
                                        style={{ width: `${marketState.trust_level * 100}%` }}
                                    />
                                </div>
                            </div>

                            <div className="text-center">
                                <div className="text-4xl font-bold text-accent-400 mb-2">
                                    {marketState.viral_coefficient.toFixed(2)}x
                                </div>
                                <div className="text-sm text-gray-400">Viral Coefficient</div>
                                <div className="text-xs text-gray-500 mt-2">
                                    {marketState.viral_coefficient > 1.3 ? '🔥 Going Viral' :
                                        marketState.viral_coefficient > 1.0 ? '📈 Growing' : '📉 Declining'}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Agent Filter */}
                <div className="card mb-6">
                    <div className="flex gap-2 flex-wrap">
                        {agentRoles.map((role) => (
                            <button
                                key={role}
                                onClick={() => setSelectedAgent(role)}
                                className={`px-4 py-2 rounded-lg transition-all ${selectedAgent === role
                                        ? 'bg-primary-500 text-white'
                                        : 'bg-white/10 text-gray-400 hover:bg-white/20'
                                    }`}
                            >
                                {role.toUpperCase()}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Agent Decisions Feed */}
                <div className="space-y-4">
                    {decisions.length === 0 ? (
                        <div className="card text-center py-12">
                            <div className="text-6xl mb-4">🤖</div>
                            <p className="text-gray-400">No agent decisions yet. Start the simulation to see agents think!</p>
                        </div>
                    ) : (
                        decisions.map((decision) => (
                            <div key={decision.id} className="card">
                                <div className="flex justify-between items-start mb-4">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-3 h-3 rounded-full ${decision.executed ? 'bg-green-500' :
                                                decision.approved ? 'bg-yellow-500' : 'bg-blue-500'
                                            }`} />
                                        <div>
                                            <div className="font-bold text-lg">
                                                {decision.agent_role.toUpperCase()}
                                            </div>
                                            <div className="text-sm text-gray-400">
                                                Tick {decision.tick} • {new Date(decision.created_at).toLocaleTimeString()}
                                            </div>
                                        </div>
                                    </div>
                                    <div className={`px-3 py-1 rounded-full text-sm ${decision.executed ? 'bg-green-500/20 text-green-400' :
                                            decision.approved ? 'bg-yellow-500/20 text-yellow-400' :
                                                'bg-blue-500/20 text-blue-400'
                                        }`}>
                                        {decision.executed ? 'Executed' : decision.approved ? 'Approved' : 'Proposed'}
                                    </div>
                                </div>

                                {/* Reasoning */}
                                {decision.reasoning && (
                                    <div className="mb-4 p-4 bg-white/5 rounded-lg">
                                        <div className="text-sm font-semibold text-gray-400 mb-2">💭 Reasoning:</div>
                                        <div className="text-sm">{decision.reasoning}</div>
                                    </div>
                                )}

                                {/* Proposed Actions */}
                                <div className="space-y-2">
                                    <div className="text-sm font-semibold text-gray-400">📋 Proposed Actions:</div>
                                    {decision.proposed_actions.map((action: any, idx: number) => (
                                        <div key={idx} className="p-3 bg-white/5 rounded-lg text-sm">
                                            <div className="font-semibold text-primary-400">{action.type}</div>
                                            <div className="text-gray-400 mt-1">
                                                {JSON.stringify(action.params, null, 2)}
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {/* Observations Summary */}
                                <details className="mt-4">
                                    <summary className="cursor-pointer text-sm text-gray-400 hover:text-white">
                                        View Observations
                                    </summary>
                                    <pre className="mt-2 p-3 bg-black/30 rounded-lg text-xs overflow-auto">
                                        {JSON.stringify(decision.observations, null, 2)}
                                    </pre>
                                </details>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </main>
    );
}
