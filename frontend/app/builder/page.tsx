'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

type IndustryTemplate = 'saas' | 'd2c' | 'manufacturing' | 'logistics' | 'fintech' | 'marketplace';

interface BlueprintData {
    name: string;
    industry: IndustryTemplate;
    initialConditions: {
        cash: number;
        monthlyBurn: number;
        headcount: number;
    };
    constraints: {
        hiringVelocityMax: number;
        workingCapitalMin: number;
    };
    policies: {
        spendLimitMonthly: number;
        approvalThreshold: number;
        riskAppetite: number;
    };
}

export default function BuilderPage() {
    const router = useRouter();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [blueprint, setBlueprint] = useState<BlueprintData>({
        name: '',
        industry: 'saas',
        initialConditions: {
            cash: 5000000,
            monthlyBurn: 200000,
            headcount: 20,
        },
        constraints: {
            hiringVelocityMax: 5,
            workingCapitalMin: 500000,
        },
        policies: {
            spendLimitMonthly: 300000,
            approvalThreshold: 100000,
            riskAppetite: 0.5,
        },
    });

    const templates: { id: IndustryTemplate; name: string; description: string }[] = [
        { id: 'saas', name: 'SaaS', description: 'Recurring revenue and churn management' },
        { id: 'd2c', name: 'D2C', description: 'Inventory, fulfillment, and customer acquisition' },
        { id: 'manufacturing', name: 'Manufacturing', description: 'Lead times, supplier reliability, safety stock' },
        { id: 'logistics', name: 'Logistics', description: 'Supply chain optimization and service levels' },
        { id: 'fintech', name: 'Fintech', description: 'Regulatory compliance and risk management' },
        { id: 'marketplace', name: 'Marketplace', description: 'Two-sided network effects and liquidity' },
    ];

    const handleSubmit = async () => {
        if (loading) return; // Prevent double-click

        setLoading(true);
        setError('');

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/v1/config/blueprints`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Idempotency-Key': `blueprint-${Date.now()}-${Math.random()}`
                },
                body: JSON.stringify({
                    name: blueprint.name || `${blueprint.industry}-company`,
                    industry: blueprint.industry,
                    initial_conditions: {
                        cash: blueprint.initialConditions.cash,
                        monthly_burn: blueprint.initialConditions.monthlyBurn,
                        headcount: blueprint.initialConditions.headcount,
                        pricing: { base: 100 },
                        margins: { gross: 0.7 },
                        capacity: {}
                    },
                    constraints: {
                        hiring_velocity_max: blueprint.constraints.hiringVelocityMax,
                        procurement_lead_time_days: { raw_materials: [7, 14] },
                        working_capital_min: blueprint.constraints.workingCapitalMin,
                        compliance_strictness: 0.8
                    },
                    policies: {
                        spend_limit_monthly: blueprint.policies.spendLimitMonthly,
                        approval_threshold: blueprint.policies.approvalThreshold,
                        max_percent_change: { pricing: 0.2, headcount: 0.3 },
                        risk_appetite: blueprint.policies.riskAppetite
                    },
                    market_exposure: {
                        volatility: 0.3,
                        seasonality: 0.1
                    }
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            const data = await response.json();
            console.log('Blueprint created:', data);

            // Success - redirect to org designer with blueprint ID
            router.push(`/org?blueprintId=${data.id}`);
        } catch (err: any) {
            console.error('Failed to create blueprint:', err);
            setError(err.message || 'Failed to create blueprint. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="min-h-screen py-12 px-4">
            <div className="max-w-4xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2 text-gradient">Company Builder</h1>
                    <p className="text-gray-400">Create your company blueprint for simulation</p>
                </div>

                {/* Progress Steps */}
                <div className="flex justify-between mb-12">
                    {[1, 2, 3, 4].map((s) => (
                        <div key={s} className="flex items-center">
                            <div
                                className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all ${s <= step
                                    ? 'bg-gradient-to-r from-primary-600 to-primary-500 text-white'
                                    : 'glass text-gray-400'
                                    }`}
                            >
                                {s}
                            </div>
                            {s < 4 && (
                                <div
                                    className={`h-1 w-24 mx-2 transition-all ${s < step ? 'bg-primary-500' : 'bg-white/20'
                                        }`}
                                ></div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Step 1: Template Selection */}
                {step === 1 && (
                    <div className="card animate-fade-in">
                        <h2 className="text-2xl font-bold mb-6">Select Industry Template</h2>
                        <div className="grid md:grid-cols-2 gap-4">
                            {templates.map((ind) => (
                                <button
                                    key={ind.id}
                                    onClick={() => setBlueprint({ ...blueprint, industry: ind.id })}
                                    className={`p-6 rounded-lg text-left transition-all ${blueprint.industry === ind.id
                                        ? 'bg-gradient-to-br from-primary-600/30 to-accent-600/30 border-2 border-primary-500'
                                        : 'glass hover:bg-white/20'
                                        }`}
                                >
                                    <h3 className="text-xl font-bold mb-2">{ind.name}</h3>
                                    <p className="text-gray-400 text-sm">{ind.description}</p>
                                </button>
                            ))}
                        </div>
                        <div className="mt-8">
                            <label className="block text-sm font-medium mb-2">Company Name</label>
                            <input
                                type="text"
                                value={blueprint.name}
                                onChange={(e) => setBlueprint({ ...blueprint, name: e.target.value })}
                                className="input w-full"
                                placeholder="Enter company name"
                            />
                        </div>
                        <div className="mt-6 flex justify-end">
                            <button
                                onClick={() => setStep(2)}
                                disabled={!blueprint.name}
                                className="btn-primary disabled:opacity-50"
                            >
                                Next
                            </button>
                        </div>
                    </div>
                )}

                {/* Step 2: Initial Conditions */}
                {step === 2 && (
                    <div className="card animate-fade-in">
                        <h2 className="text-2xl font-bold mb-6">Initial Conditions</h2>
                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Initial Cash: ${blueprint.initialConditions.cash.toLocaleString()}
                                </label>
                                <input
                                    type="range"
                                    min="1000000"
                                    max="50000000"
                                    step="500000"
                                    value={blueprint.initialConditions.cash}
                                    onChange={(e) =>
                                        setBlueprint({
                                            ...blueprint,
                                            initialConditions: {
                                                ...blueprint.initialConditions,
                                                cash: parseInt(e.target.value),
                                            },
                                        })
                                    }
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Monthly Burn: ${blueprint.initialConditions.monthlyBurn.toLocaleString()}
                                </label>
                                <input
                                    type="range"
                                    min="50000"
                                    max="1000000"
                                    step="10000"
                                    value={blueprint.initialConditions.monthlyBurn}
                                    onChange={(e) =>
                                        setBlueprint({
                                            ...blueprint,
                                            initialConditions: {
                                                ...blueprint.initialConditions,
                                                monthlyBurn: parseInt(e.target.value),
                                            },
                                        })
                                    }
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Initial Headcount: {blueprint.initialConditions.headcount}
                                </label>
                                <input
                                    type="range"
                                    min="5"
                                    max="200"
                                    step="5"
                                    value={blueprint.initialConditions.headcount}
                                    onChange={(e) =>
                                        setBlueprint({
                                            ...blueprint,
                                            initialConditions: {
                                                ...blueprint.initialConditions,
                                                headcount: parseInt(e.target.value),
                                            },
                                        })
                                    }
                                    className="w-full"
                                />
                            </div>
                        </div>
                        <div className="mt-6 flex justify-between">
                            <button onClick={() => setStep(1)} className="btn-secondary">
                                Back
                            </button>
                            <button onClick={() => setStep(3)} className="btn-primary">
                                Next
                            </button>
                        </div>
                    </div>
                )}

                {/* Step 3: Constraints */}
                {step === 3 && (
                    <div className="card animate-fade-in">
                        <h2 className="text-2xl font-bold mb-6">Operational Constraints</h2>
                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Max Hiring Velocity (per month): {blueprint.constraints.hiringVelocityMax}
                                </label>
                                <input
                                    type="range"
                                    min="1"
                                    max="20"
                                    value={blueprint.constraints.hiringVelocityMax}
                                    onChange={(e) =>
                                        setBlueprint({
                                            ...blueprint,
                                            constraints: {
                                                ...blueprint.constraints,
                                                hiringVelocityMax: parseInt(e.target.value),
                                            },
                                        })
                                    }
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Minimum Working Capital: ${blueprint.constraints.workingCapitalMin.toLocaleString()}
                                </label>
                                <input
                                    type="range"
                                    min="100000"
                                    max="2000000"
                                    step="100000"
                                    value={blueprint.constraints.workingCapitalMin}
                                    onChange={(e) =>
                                        setBlueprint({
                                            ...blueprint,
                                            constraints: {
                                                ...blueprint.constraints,
                                                workingCapitalMin: parseInt(e.target.value),
                                            },
                                        })
                                    }
                                    className="w-full"
                                />
                            </div>
                        </div>
                        <div className="mt-6 flex justify-between">
                            <button onClick={() => setStep(2)} className="btn-secondary">
                                Back
                            </button>
                            <button onClick={() => setStep(4)} className="btn-primary">
                                Next
                            </button>
                        </div>
                    </div>
                )}

                {/* Step 4: Policies */}
                {step === 4 && (
                    <div className="card animate-fade-in">
                        <h2 className="text-2xl font-bold mb-6">Policies & Guardrails</h2>
                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Monthly Spend Limit: ${blueprint.policies.spendLimitMonthly.toLocaleString()}
                                </label>
                                <input
                                    type="range"
                                    min="100000"
                                    max="1000000"
                                    step="50000"
                                    value={blueprint.policies.spendLimitMonthly}
                                    onChange={(e) =>
                                        setBlueprint({
                                            ...blueprint,
                                            policies: {
                                                ...blueprint.policies,
                                                spendLimitMonthly: parseInt(e.target.value),
                                            },
                                        })
                                    }
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Approval Threshold: ${blueprint.policies.approvalThreshold.toLocaleString()}
                                </label>
                                <input
                                    type="range"
                                    min="10000"
                                    max="500000"
                                    step="10000"
                                    value={blueprint.policies.approvalThreshold}
                                    onChange={(e) =>
                                        setBlueprint({
                                            ...blueprint,
                                            policies: {
                                                ...blueprint.policies,
                                                approvalThreshold: parseInt(e.target.value),
                                            },
                                        })
                                    }
                                    className="w-full"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Risk Appetite: {(blueprint.policies.riskAppetite * 100).toFixed(0)}%
                                </label>
                                <input
                                    type="range"
                                    min="0"
                                    max="1"
                                    step="0.1"
                                    value={blueprint.policies.riskAppetite}
                                    onChange={(e) =>
                                        setBlueprint({
                                            ...blueprint,
                                            policies: {
                                                ...blueprint.policies,
                                                riskAppetite: parseFloat(e.target.value),
                                            },
                                        })
                                    }
                                    className="w-full"
                                />
                            </div>
                        </div>
                        <div className="flex justify-between mt-8">
                            {step > 1 && (
                                <button onClick={() => setStep(step - 1)} className="btn-secondary">
                                    Back
                                </button>
                            )}
                            {step < 4 ? (
                                <button
                                    onClick={() => setStep(step + 1)}
                                    disabled={step === 1 && !blueprint.name}
                                    className="btn-primary ml-auto disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Next
                                </button>
                            ) : (
                                <button
                                    onClick={handleSubmit}
                                    disabled={loading || !blueprint.name}
                                    className="btn-primary ml-auto disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {loading ? 'Creating...' : 'Create Blueprint'}
                                </button>
                            )}
                        </div>

                        {error && (
                            <div className="mt-4 p-4 bg-red-500/20 border border-red-500 rounded-lg text-red-400">
                                {error}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </main>
    );
}
