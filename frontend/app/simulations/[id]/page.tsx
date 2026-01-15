'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface SimulationMetrics {
    current_time: string;
    cash: number;
    runway_months: number;
    revenue_monthly: number;
    costs_monthly: number;
    headcount: number;
    growth_rate: number;
    service_level: number;
    compliance_score: number;
}

export default function SimulationPage({ params }: { params: { id: string } }) {
    const [metrics, setMetrics] = useState<SimulationMetrics | null>(null);
    const [events, setEvents] = useState<any[]>([]);

    useEffect(() => {
        fetchState();
        fetchEvents();
    }, []);

    const fetchState = async () => {
        const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${url}/api/v1/simulation/runs/${params.id}/state`);
        const data = await response.json();
        setMetrics(data.metrics);
        setStatus(data.status);
    };

    const fetchEvents = async () => {
        const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        // Mocking events endpoint for now or using the one from agent-data
        // We'll use the event-responses endpoint to deduce what happened
        try {
            const response = await fetch(`${url}/api/v1/agent-data/event-responses/${params.id}`);
            if (response.ok) {
                const data = await response.json();
                setEvents(data);
            }
        } catch (e) {
            console.error("Failed to fetch events", e);
        }
    };

    const startSimulation = async () => {
        const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        await fetch(`${url}/api/v1/simulation/runs/${params.id}/start`, {
            method: 'POST',
        });
        setStatus('running');
    };

    const tickSimulation = async (ticks: number = 1) => {
        const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${url}/api/v1/simulation/runs/${params.id}/tick`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticks }),
        });
        const data = await response.json();
        setMetrics(data.metrics);
        setStatus(data.status);

        // Add to history
        setHistory((prev) => {
            const safePrev = Array.isArray(prev) ? prev : [];
            return [...safePrev, { ...data.metrics, current_time: data.current_time }];
        });
        fetchEvents(); // Refresh events
    };

    if (!metrics) {
        return (
            <main className="min-h-screen py-12 px-4">
                <div className="max-w-7xl mx-auto">
                    <div className="card text-center">
                        <div className="animate-pulse">Loading simulation...</div>
                    </div>
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen py-12 px-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-4xl font-bold text-gradient">Simulation Dashboard</h1>
                        <p className="text-gray-400 mt-2">Run ID: {params.id}</p>
                    </div>
                    <div className="flex space-x-4">
                        {status === 'created' && (
                            <button onClick={startSimulation} className="btn-primary">
                                Start Simulation
                            </button>
                        )}
                        {status === 'running' && (
                            <>
                                <button onClick={() => tickSimulation(1)} className="btn-secondary">
                                    Step (1 tick)
                                </button>
                                <button onClick={() => tickSimulation(10)} className="btn-primary">
                                    Run (10 ticks)
                                </button>
                            </>
                        )}
                        {status === 'completed' && (
                            <div className="px-6 py-3 glass rounded-lg">
                                <span className="text-green-400 font-medium">✓ Completed</span>
                            </div>
                        )}
                    </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid md:grid-cols-4 gap-6 mb-8">
                    <div className="card">
                        <div className="text-sm text-gray-400 mb-1">Cash</div>
                        <div className="text-3xl font-bold text-gradient">
                            ${(metrics.cash / 1000000).toFixed(2)}M
                        </div>
                        <div className="text-sm text-gray-400 mt-2">
                            Runway: {metrics.runway_months.toFixed(1)} months
                        </div>
                    </div>

                    <div className="card">
                        <div className="text-sm text-gray-400 mb-1">Revenue (Monthly)</div>
                        <div className="text-3xl font-bold text-green-400">
                            ${(metrics.revenue_monthly / 1000).toFixed(0)}K
                        </div>
                        <div className="text-sm text-gray-400 mt-2">
                            Growth: {(metrics.growth_rate * 100).toFixed(1)}%
                        </div>
                    </div>

                    <div className="card">
                        <div className="text-sm text-gray-400 mb-1">Costs (Monthly)</div>
                        <div className="text-3xl font-bold text-red-400">
                            ${(metrics.costs_monthly / 1000).toFixed(0)}K
                        </div>
                        <div className="text-sm text-gray-400 mt-2">
                            Headcount: {metrics.headcount}
                        </div>
                    </div>

                    <div className="card">
                        <div className="text-sm text-gray-400 mb-1">Service Level</div>
                        <div className="text-3xl font-bold text-blue-400">
                            {(metrics.service_level * 100).toFixed(1)}%
                        </div>
                        <div className="text-sm text-gray-400 mt-2">
                            Compliance: {(metrics.compliance_score * 100).toFixed(0)}%
                        </div>
                    </div>
                </div>

                {/* Charts */}
                {Array.isArray(history) && history.length > 0 && (
                    <div className="card mb-8">
                        <h2 className="text-2xl font-bold mb-6">Financial Metrics Over Time</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={history}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis
                                    dataKey="current_time"
                                    stroke="#9CA3AF"
                                    tickFormatter={(str) => new Date(str).toLocaleDateString()}
                                />
                                <YAxis stroke="#9CA3AF" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                        border: '1px solid rgba(255, 255, 255, 0.2)',
                                        borderRadius: '8px',
                                    }}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="cash"
                                    stroke="#0ea5e9"
                                    strokeWidth={2}
                                    name="Cash"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="revenue_monthly"
                                    stroke="#10b981"
                                    strokeWidth={2}
                                    name="Revenue"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="costs_monthly"
                                    stroke="#ef4444"
                                    strokeWidth={2}
                                    name="Costs"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                )}

                {/* Current State */}
                <div className="grid md:grid-cols-2 gap-6">
                    <div className="card">
                        <h2 className="text-2xl font-bold mb-4">Current Status</h2>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <div className="text-sm text-gray-400">Simulation Time</div>
                                <div className="text-lg font-medium">
                                    {new Date(metrics.current_time).toLocaleDateString()}
                                </div>
                            </div>
                            <div>
                                <div className="text-sm text-gray-400">Status</div>
                                <div className="text-lg font-medium capitalize">{status}</div>
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <h2 className="text-2xl font-bold mb-4">World Events & Alerts</h2>
                        <div className="space-y-3 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                            {events.length === 0 ? (
                                <p className="text-gray-500 italic">No significant events yet...</p>
                            ) : (
                                events.map((evt, i) => (
                                    <div key={i} className="p-3 glass rounded border-l-4 border-yellow-500 bg-white/5">
                                        <div className="flex justify-between items-start">
                                            <span className="text-xs font-mono text-gray-400">Tick {evt.tick}</span>
                                            <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 capitalize">{evt.agent_role}</span>
                                        </div>
                                        <p className="mt-1 text-sm">{evt.response_text || 'Reacted to market changes'}</p>
                                        <div className="mt-2 text-xs flex flex-wrap gap-1">
                                            {Object.entries(evt.actions_taken || {}).map(([k, v]) => (
                                                <span key={k} className="px-1.5 py-0.5 bg-gray-700/50 rounded text-gray-300">{k}: {String(v)}</span>
                                            ))}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}
