'use client';

import { useState, useEffect } from 'react';

export default function ReplayPage({ params }: { params: { id: string } }) {
    const [auditEntries, setAuditEntries] = useState<any[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);

    useEffect(() => {
        fetchAuditTrail();
    }, []);

    useEffect(() => {
        if (isPlaying && currentIndex < auditEntries.length - 1) {
            const timer = setTimeout(() => {
                setCurrentIndex(currentIndex + 1);
            }, 1000);
            return () => clearTimeout(timer);
        } else if (currentIndex >= auditEntries.length - 1) {
            setIsPlaying(false);
        }
    }, [isPlaying, currentIndex, auditEntries.length]);

    const fetchAuditTrail = async () => {
        const response = await fetch(
            `${process.env.API_URL}/api/v1/simulation/runs/${params.id}/audit`
        );
        const data = await response.json();
        setAuditEntries(data.entries || []);
    };

    const currentEntry = auditEntries[currentIndex];

    return (
        <main className="min-h-screen py-12 px-4">
            <div className="max-w-7xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-gradient">Simulation Replay</h1>
                    <p className="text-gray-400 mt-2">Deterministic playback of run {params.id}</p>
                </div>

                {/* Playback Controls */}
                <div className="card mb-8">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-4">
                            <button
                                onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
                                disabled={currentIndex === 0}
                                className="btn-secondary disabled:opacity-50"
                            >
                                ← Previous
                            </button>
                            <button
                                onClick={() => setIsPlaying(!isPlaying)}
                                className="btn-primary"
                            >
                                {isPlaying ? 'Pause' : 'Play'}
                            </button>
                            <button
                                onClick={() =>
                                    setCurrentIndex(Math.min(auditEntries.length - 1, currentIndex + 1))
                                }
                                disabled={currentIndex >= auditEntries.length - 1}
                                className="btn-secondary disabled:opacity-50"
                            >
                                Next →
                            </button>
                        </div>
                        <div className="text-sm text-gray-400">
                            Entry {currentIndex + 1} of {auditEntries.length}
                        </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-white/10 rounded-full h-2">
                        <div
                            className="bg-gradient-to-r from-primary-500 to-accent-500 h-2 rounded-full transition-all"
                            style={{
                                width: `${((currentIndex + 1) / auditEntries.length) * 100}%`,
                            }}
                        ></div>
                    </div>
                </div>

                {/* Current Entry */}
                {currentEntry && (
                    <div className="grid md:grid-cols-2 gap-8">
                        {/* Entry Details */}
                        <div className="card">
                            <h2 className="text-2xl font-bold mb-4">Entry Details</h2>
                            <div className="space-y-3">
                                <div>
                                    <div className="text-sm text-gray-400">Sequence</div>
                                    <div className="font-medium">{currentEntry.sequence}</div>
                                </div>
                                <div>
                                    <div className="text-sm text-gray-400">Simulation Time</div>
                                    <div className="font-medium">
                                        {new Date(currentEntry.sim_time).toLocaleString()}
                                    </div>
                                </div>
                                <div>
                                    <div className="text-sm text-gray-400">Entry Type</div>
                                    <div className="font-medium capitalize">
                                        {currentEntry.entry_type.replace('_', ' ')}
                                    </div>
                                </div>
                                {currentEntry.agent_role && (
                                    <div>
                                        <div className="text-sm text-gray-400">Agent</div>
                                        <div className="font-medium uppercase">{currentEntry.agent_role}</div>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Action/State */}
                        <div className="card">
                            <h2 className="text-2xl font-bold mb-4">Action</h2>
                            {currentEntry.action && (
                                <div className="glass p-4 rounded-lg">
                                    <div className="font-bold capitalize mb-2">
                                        {currentEntry.action.type?.replace('_', ' ')}
                                    </div>
                                    <pre className="text-sm text-gray-300 overflow-auto">
                                        {JSON.stringify(currentEntry.action.params, null, 2)}
                                    </pre>
                                </div>
                            )}
                        </div>

                        {/* State Before/After */}
                        {currentEntry.state_before && currentEntry.state_after && (
                            <>
                                <div className="card">
                                    <h2 className="text-2xl font-bold mb-4">State Before</h2>
                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <span className="text-gray-400">Cash</span>
                                            <span className="font-medium">
                                                ${currentEntry.state_before.cash?.toLocaleString()}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-400">Headcount</span>
                                            <span className="font-medium">{currentEntry.state_before.headcount}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="card">
                                    <h2 className="text-2xl font-bold mb-4">State After</h2>
                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <span className="text-gray-400">Cash</span>
                                            <span className="font-medium">
                                                ${currentEntry.state_after.cash?.toLocaleString()}
                                            </span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-gray-400">Headcount</span>
                                            <span className="font-medium">{currentEntry.state_after.headcount}</span>
                                        </div>
                                    </div>
                                </div>
                            </>
                        )}

                        {/* Policy Check */}
                        {currentEntry.policy_check && (
                            <div className="card md:col-span-2">
                                <h2 className="text-2xl font-bold mb-4">Policy Check</h2>
                                <div className="glass p-4 rounded-lg">
                                    <div className="flex items-center space-x-2 mb-2">
                                        <span
                                            className={`font-bold ${currentEntry.policy_check.decision === 'approve'
                                                    ? 'text-green-400'
                                                    : currentEntry.policy_check.decision === 'deny'
                                                        ? 'text-red-400'
                                                        : 'text-yellow-400'
                                                }`}
                                        >
                                            {currentEntry.policy_check.decision?.toUpperCase()}
                                        </span>
                                    </div>
                                    <div className="text-sm text-gray-300">
                                        {currentEntry.policy_check.reason}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </main>
    );
}
