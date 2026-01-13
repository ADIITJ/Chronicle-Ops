'use client';

import { useState } from 'react';

interface Signal {
    release_time: string;
    type: string;
    content: string;
}

interface CustomEvent {
    timestamp: string;
    event_type: string;
    severity: number;
    duration_days: number;
    affected_areas: string[];
    signals: Signal[];
    parameter_impacts: { [key: string]: number };
}

export default function TimelineStudioPage() {
    const [startDate, setStartDate] = useState('2020-01-01');
    const [endDate, setEndDate] = useState('2026-12-31');
    const [selectedPacks, setSelectedPacks] = useState<string[]>(['historical_2010_2026']);
    const [customEvents, setCustomEvents] = useState<CustomEvent[]>([]);
    const [showEventBuilder, setShowEventBuilder] = useState(false);

    const eventPacks = [
        { id: 'historical_2010_2026', name: 'Historical Events (2010-2026)', count: 11 },
        { id: 'macro_events', name: 'Macro Economic Events', count: 8 },
        { id: 'tech_disruptions', name: 'Technology Disruptions', count: 6 },
        { id: 'regulatory_changes', name: 'Regulatory Changes', count: 5 },
        { id: 'supply_chain', name: 'Supply Chain Events', count: 7 },
    ];

    const [newEvent, setNewEvent] = useState<Partial<CustomEvent>>({
        timestamp: new Date().toISOString().split('T')[0],
        event_type: 'custom',
        severity: 0.5,
        duration_days: 90,
        affected_areas: [],
        signals: [],
        parameter_impacts: {},
    });

    const addCustomEvent = () => {
        if (newEvent.timestamp && newEvent.event_type) {
            setCustomEvents([...customEvents, newEvent as CustomEvent]);
            setNewEvent({
                timestamp: new Date().toISOString().split('T')[0],
                event_type: 'custom',
                severity: 0.5,
                duration_days: 90,
                affected_areas: [],
                signals: [],
                parameter_impacts: {},
            });
            setShowEventBuilder(false);
        }
    };

    const handleSubmit = async () => {
        const response = await fetch(`${process.env.API_URL}/api/v1/config/timelines`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: 'Custom Timeline',
                start_date: startDate,
                end_date: endDate,
                events: customEvents,
            }),
        });

        if (response.ok) {
            const data = await response.json();
            alert(`Timeline created: ${data.id}`);
        }
    };

    return (
        <main className="min-h-screen py-12 px-4">
            <div className="max-w-6xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2 text-gradient">Timeline Studio</h1>
                    <p className="text-gray-400">Configure event timeline for your simulation</p>
                </div>

                {/* Date Range */}
                <div className="card mb-8">
                    <h2 className="text-2xl font-bold mb-4">Simulation Period</h2>
                    <div className="grid md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">Start Date</label>
                            <input
                                type="date"
                                value={startDate}
                                onChange={(e) => setStartDate(e.target.value)}
                                className="input w-full"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">End Date</label>
                            <input
                                type="date"
                                value={endDate}
                                onChange={(e) => setEndDate(e.target.value)}
                                className="input w-full"
                            />
                        </div>
                    </div>
                </div>

                {/* Event Packs */}
                <div className="card mb-8">
                    <h2 className="text-2xl font-bold mb-4">Event Packs</h2>
                    <div className="space-y-3">
                        {eventPacks.map((pack) => (
                            <label key={pack.id} className="flex items-center space-x-3 p-3 glass rounded-lg hover:bg-white/20 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={selectedPacks.includes(pack.id)}
                                    onChange={(e) => {
                                        if (e.target.checked) {
                                            setSelectedPacks([...selectedPacks, pack.id]);
                                        } else {
                                            setSelectedPacks(selectedPacks.filter((p) => p !== pack.id));
                                        }
                                    }}
                                    className="rounded"
                                />
                                <div className="flex-1">
                                    <div className="font-medium">{pack.name}</div>
                                    <div className="text-sm text-gray-400">{pack.count} events</div>
                                </div>
                            </label>
                        ))}
                    </div>
                </div>

                {/* Custom Events */}
                <div className="card mb-8">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-2xl font-bold">Custom Events</h2>
                        <button
                            onClick={() => setShowEventBuilder(!showEventBuilder)}
                            className="btn-secondary"
                        >
                            {showEventBuilder ? 'Cancel' : 'Add Event'}
                        </button>
                    </div>

                    {showEventBuilder && (
                        <div className="glass p-6 rounded-lg mb-4">
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2">Event Date</label>
                                    <input
                                        type="date"
                                        value={newEvent.timestamp}
                                        onChange={(e) => setNewEvent({ ...newEvent, timestamp: e.target.value })}
                                        className="input w-full"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">Event Type</label>
                                    <select
                                        value={newEvent.event_type}
                                        onChange={(e) => setNewEvent({ ...newEvent, event_type: e.target.value })}
                                        className="input w-full"
                                    >
                                        <option value="custom">Custom</option>
                                        <option value="competitor_launch">Competitor Launch</option>
                                        <option value="market_shift">Market Shift</option>
                                        <option value="regulatory">Regulatory Change</option>
                                        <option value="supply_disruption">Supply Disruption</option>
                                        <option value="tech_breakthrough">Tech Breakthrough</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Severity: {((newEvent.severity || 0) * 100).toFixed(0)}%
                                    </label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={newEvent.severity}
                                        onChange={(e) =>
                                            setNewEvent({ ...newEvent, severity: parseFloat(e.target.value) })
                                        }
                                        className="w-full"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Duration: {newEvent.duration_days} days
                                    </label>
                                    <input
                                        type="range"
                                        min="7"
                                        max="730"
                                        step="7"
                                        value={newEvent.duration_days}
                                        onChange={(e) =>
                                            setNewEvent({ ...newEvent, duration_days: parseInt(e.target.value) })
                                        }
                                        className="w-full"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">Affected Areas</label>
                                    <div className="grid md:grid-cols-3 gap-2">
                                        {['global', 'tech', 'finance', 'manufacturing', 'logistics', 'saas'].map((area) => (
                                            <label key={area} className="flex items-center space-x-2">
                                                <input
                                                    type="checkbox"
                                                    checked={newEvent.affected_areas?.includes(area)}
                                                    onChange={(e) => {
                                                        const areas = newEvent.affected_areas || [];
                                                        if (e.target.checked) {
                                                            setNewEvent({ ...newEvent, affected_areas: [...areas, area] });
                                                        } else {
                                                            setNewEvent({
                                                                ...newEvent,
                                                                affected_areas: areas.filter((a) => a !== area),
                                                            });
                                                        }
                                                    }}
                                                    className="rounded"
                                                />
                                                <span className="text-sm capitalize">{area}</span>
                                            </label>
                                        ))}
                                    </div>
                                </div>

                                <button onClick={addCustomEvent} className="btn-primary w-full">
                                    Add Event
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Event List */}
                    <div className="space-y-3">
                        {customEvents.map((event, index) => (
                            <div key={index} className="glass p-4 rounded-lg">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <div className="font-bold capitalize">{event.event_type}</div>
                                        <div className="text-sm text-gray-400">
                                            {new Date(event.timestamp).toLocaleDateString()} • Severity:{' '}
                                            {(event.severity * 100).toFixed(0)}% • {event.duration_days} days
                                        </div>
                                        <div className="text-sm text-gray-400 mt-1">
                                            Areas: {event.affected_areas.join(', ')}
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setCustomEvents(customEvents.filter((_, i) => i !== index))}
                                        className="text-red-400 hover:text-red-300"
                                    >
                                        Remove
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Submit */}
                <button onClick={handleSubmit} className="btn-primary w-full">
                    Save Timeline
                </button>
            </div>
        </main>
    );
}
