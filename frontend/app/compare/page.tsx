'use client';

import { useState, useEffect } from 'react';

export default function ComparePage() {
    const [run1Id, setRun1Id] = useState('');
    const [run2Id, setRun2Id] = useState('');
    const [run1Data, setRun1Data] = useState<any>(null);
    const [run2Data, setRun2Data] = useState<any>(null);

    const loadRun = async (runId: string, setData: Function) => {
        const response = await fetch(`${process.env.API_URL}/api/v1/simulation/runs/${runId}/state`);
        const data = await response.json();
        setData(data);
    };

    const compareRuns = () => {
        if (run1Id && run2Id) {
            loadRun(run1Id, setRun1Data);
            loadRun(run2Id, setRun2Data);
        }
    };

    const calculateDiff = (val1: number, val2: number) => {
        const diff = val2 - val1;
        const percent = ((diff / val1) * 100).toFixed(1);
        return { diff, percent };
    };

    return (
        <main className="min-h-screen py-12 px-4">
            <div className="max-w-7xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-gradient">Compare Simulations</h1>
                    <p className="text-gray-400 mt-2">Side-by-side comparison of simulation runs</p>
                </div>

                {/* Input */}
                <div className="card mb-8">
                    <div className="grid md:grid-cols-3 gap-4">
                        <input
                            type="text"
                            value={run1Id}
                            onChange={(e) => setRun1Id(e.target.value)}
                            placeholder="Run 1 ID"
                            className="input"
                        />
                        <input
                            type="text"
                            value={run2Id}
                            onChange={(e) => setRun2Id(e.target.value)}
                            placeholder="Run 2 ID"
                            className="input"
                        />
                        <button onClick={compareRuns} className="btn-primary">
                            Compare
                        </button>
                    </div>
                </div>

                {/* Comparison */}
                {run1Data && run2Data && (
                    <div className="space-y-8">
                        {/* Metrics Comparison */}
                        <div className="card">
                            <h2 className="text-2xl font-bold mb-6">Metrics Comparison</h2>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead>
                                        <tr className="border-b border-white/20">
                                            <th className="text-left py-3 px-4">Metric</th>
                                            <th className="text-right py-3 px-4">Run 1</th>
                                            <th className="text-right py-3 px-4">Run 2</th>
                                            <th className="text-right py-3 px-4">Difference</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {[
                                            { key: 'cash', label: 'Cash', format: (v: number) => `$${(v / 1000000).toFixed(2)}M` },
                                            { key: 'runway_months', label: 'Runway (months)', format: (v: number) => v.toFixed(1) },
                                            { key: 'revenue_monthly', label: 'Revenue (monthly)', format: (v: number) => `$${(v / 1000).toFixed(0)}K` },
                                            { key: 'costs_monthly', label: 'Costs (monthly)', format: (v: number) => `$${(v / 1000).toFixed(0)}K` },
                                            { key: 'headcount', label: 'Headcount', format: (v: number) => v.toString() },
                                            { key: 'service_level', label: 'Service Level', format: (v: number) => `${(v * 100).toFixed(1)}%` },
                                        ].map((metric) => {
                                            const val1 = run1Data.metrics[metric.key];
                                            const val2 = run2Data.metrics[metric.key];
                                            const { diff, percent } = calculateDiff(val1, val2);
                                            const isPositive = diff > 0;

                                            return (
                                                <tr key={metric.key} className="border-b border-white/10">
                                                    <td className="py-3 px-4">{metric.label}</td>
                                                    <td className="text-right py-3 px-4">{metric.format(val1)}</td>
                                                    <td className="text-right py-3 px-4">{metric.format(val2)}</td>
                                                    <td className={`text-right py-3 px-4 font-medium ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                                                        {isPositive ? '+' : ''}{percent}%
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        {/* Status Comparison */}
                        <div className="grid md:grid-cols-2 gap-8">
                            <div className="card">
                                <h3 className="text-xl font-bold mb-4">Run 1</h3>
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">Status</span>
                                        <span className="font-medium capitalize">{run1Data.status}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">Current Time</span>
                                        <span className="font-medium">
                                            {run1Data.metrics.current_time
                                                ? new Date(run1Data.metrics.current_time).toLocaleDateString()
                                                : 'N/A'}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div className="card">
                                <h3 className="text-xl font-bold mb-4">Run 2</h3>
                                <div className="space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">Status</span>
                                        <span className="font-medium capitalize">{run2Data.status}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-400">Current Time</span>
                                        <span className="font-medium">
                                            {run2Data.metrics.current_time
                                                ? new Date(run2Data.metrics.current_time).toLocaleDateString()
                                                : 'N/A'}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
