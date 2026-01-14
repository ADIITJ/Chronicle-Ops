'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

interface MarketHistory {
    tick: number;
    sentiment_score: number;
    awareness_level: number;
    trust_level: number;
    viral_coefficient: number;
    demand_multiplier: number;
}

export default function MarketDashboardPage() {
    const params = useParams();
    const runId = params.id as string;

    const [history, setHistory] = useState<MarketHistory[]>([]);
    const [currentState, setCurrentState] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchMarketData();
        const interval = setInterval(fetchMarketData, 3000);
        return () => clearInterval(interval);
    }, [runId]);

    const fetchMarketData = async () => {
        try {
            const res = await fetch(`/api/v1/simulation/runs/${runId}/market-history`);
            if (res.ok) {
                const data = await res.json();
                setHistory(data.history || []);
                setCurrentState(data.current || null);
                setLoading(false);
            }
        } catch (error) {
            console.error('Failed to fetch market data:', error);
            setLoading(false);
        }
    };

    const sentimentChartData = {
        labels: history.map(h => `Tick ${h.tick}`),
        datasets: [
            {
                label: 'Market Sentiment',
                data: history.map(h => h.sentiment_score * 100),
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
            },
            {
                label: 'Brand Awareness',
                data: history.map(h => h.awareness_level * 100),
                borderColor: 'rgb(168, 85, 247)',
                backgroundColor: 'rgba(168, 85, 247, 0.1)',
                tension: 0.4,
            },
            {
                label: 'Consumer Trust',
                data: history.map(h => h.trust_level * 100),
                borderColor: 'rgb(34, 197, 94)',
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                tension: 0.4,
            },
        ],
    };

    const viralChartData = {
        labels: history.map(h => `Tick ${h.tick}`),
        datasets: [
            {
                label: 'Viral Coefficient',
                data: history.map(h => h.viral_coefficient),
                borderColor: 'rgb(236, 72, 153)',
                backgroundColor: 'rgba(236, 72, 153, 0.1)',
                tension: 0.4,
            },
            {
                label: 'Demand Multiplier',
                data: history.map(h => h.demand_multiplier),
                borderColor: 'rgb(251, 146, 60)',
                backgroundColor: 'rgba(251, 146, 60, 0.1)',
                tension: 0.4,
            },
        ],
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top' as const,
                labels: {
                    color: 'rgb(156, 163, 175)',
                },
            },
        },
        scales: {
            y: {
                ticks: { color: 'rgb(156, 163, 175)' },
                grid: { color: 'rgba(255, 255, 255, 0.1)' },
            },
            x: {
                ticks: { color: 'rgb(156, 163, 175)' },
                grid: { color: 'rgba(255, 255, 255, 0.1)' },
            },
        },
    };

    if (loading) {
        return (
            <main className="min-h-screen py-12 px-4">
                <div className="max-w-7xl mx-auto">
                    <div className="card text-center">
                        <div className="animate-pulse">Loading market data...</div>
                    </div>
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen py-8 px-4">
            <div className="max-w-7xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-gradient">Market Dashboard</h1>
                    <p className="text-gray-400 mt-2">Population sentiment and market dynamics</p>
                </div>

                {/* Current State Cards */}
                {currentState && (
                    <div className="grid md:grid-cols-4 gap-6 mb-8">
                        <div className="card text-center">
                            <div className="text-5xl mb-4">
                                {currentState.sentiment_score > 0.7 ? '😊' :
                                    currentState.sentiment_score > 0.4 ? '😐' : '😞'}
                            </div>
                            <div className="text-3xl font-bold text-gradient mb-2">
                                {(currentState.sentiment_score * 100).toFixed(0)}%
                            </div>
                            <div className="text-sm text-gray-400">Market Sentiment</div>
                        </div>

                        <div className="card text-center">
                            <div className="text-5xl mb-4">📢</div>
                            <div className="text-3xl font-bold text-blue-400 mb-2">
                                {(currentState.awareness_level * 100).toFixed(0)}%
                            </div>
                            <div className="text-sm text-gray-400">Brand Awareness</div>
                        </div>

                        <div className="card text-center">
                            <div className="text-5xl mb-4">🤝</div>
                            <div className="text-3xl font-bold text-purple-400 mb-2">
                                {(currentState.trust_level * 100).toFixed(0)}%
                            </div>
                            <div className="text-sm text-gray-400">Consumer Trust</div>
                        </div>

                        <div className="card text-center">
                            <div className="text-5xl mb-4">
                                {currentState.viral_coefficient > 1.3 ? '🔥' :
                                    currentState.viral_coefficient > 1.0 ? '📈' : '📉'}
                            </div>
                            <div className="text-3xl font-bold text-accent-400 mb-2">
                                {currentState.viral_coefficient.toFixed(2)}x
                            </div>
                            <div className="text-sm text-gray-400">Viral Coefficient</div>
                        </div>
                    </div>
                )}

                {/* Charts */}
                <div className="space-y-6">
                    <div className="card">
                        <h2 className="text-2xl font-bold mb-6">Sentiment & Trust Trends</h2>
                        <Line data={sentimentChartData} options={chartOptions} />
                    </div>

                    <div className="card">
                        <h2 className="text-2xl font-bold mb-6">Viral Growth & Demand</h2>
                        <Line data={viralChartData} options={chartOptions} />
                    </div>
                </div>

                {/* Market Dynamics Breakdown */}
                {currentState?.market_dynamics && (
                    <div className="card mt-6">
                        <h2 className="text-2xl font-bold mb-6">Current Market Dynamics</h2>
                        <div className="grid md:grid-cols-3 gap-4">
                            {Object.entries(currentState.market_dynamics).map(([key, value]: [string, any]) => (
                                <div key={key} className="p-4 bg-white/5 rounded-lg">
                                    <div className="text-sm text-gray-400 mb-1">
                                        {key.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                                    </div>
                                    <div className="text-2xl font-bold text-primary-400">
                                        {typeof value === 'number' ? value.toFixed(3) : value}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
