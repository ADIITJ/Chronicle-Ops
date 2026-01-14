'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function SimulationsListPage() {
    const router = useRouter();
    const [runs, setRuns] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchRuns();
    }, []);

    const fetchRuns = async () => {
        try {
            // In production, this would fetch from API
            // For now, show empty state
            setRuns([]);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch runs:', error);
            setLoading(false);
        }
    };

    const createNewRun = () => {
        router.push('/builder');
    };

    if (loading) {
        return (
            <main className="min-h-screen py-12 px-4">
                <div className="max-w-7xl mx-auto">
                    <div className="card text-center">
                        <div className="animate-pulse">Loading simulations...</div>
                    </div>
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen py-12 px-4">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-4xl font-bold text-gradient">Simulations</h1>
                        <p className="text-gray-400 mt-2">Manage and monitor your simulation runs</p>
                    </div>
                    <button onClick={createNewRun} className="btn-primary">
                        + New Simulation
                    </button>
                </div>

                {runs.length === 0 ? (
                    <div className="card text-center py-16">
                        <div className="max-w-md mx-auto">
                            <div className="text-6xl mb-4">🚀</div>
                            <h2 className="text-2xl font-bold mb-4">No Simulations Yet</h2>
                            <p className="text-gray-400 mb-8">
                                Create your first simulation to start exploring autonomous company dynamics
                            </p>
                            <button onClick={createNewRun} className="btn-primary">
                                Create First Simulation
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {runs.map((run) => (
                            <div
                                key={run.id}
                                className="card cursor-pointer hover:scale-105 transition-transform"
                                onClick={() => router.push(`/simulations/${run.id}`)}
                            >
                                <div className="flex justify-between items-start mb-4">
                                    <h3 className="text-xl font-bold">{run.name}</h3>
                                    <span
                                        className={`px-3 py-1 rounded-full text-sm ${run.status === 'running'
                                                ? 'bg-green-500/20 text-green-400'
                                                : run.status === 'completed'
                                                    ? 'bg-blue-500/20 text-blue-400'
                                                    : 'bg-gray-500/20 text-gray-400'
                                            }`}
                                    >
                                        {run.status}
                                    </span>
                                </div>
                                <div className="space-y-2 text-sm text-gray-400">
                                    <div className="flex justify-between">
                                        <span>Industry</span>
                                        <span className="text-white">{run.industry}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Created</span>
                                        <span className="text-white">
                                            {new Date(run.created_at).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </main>
    );
}
