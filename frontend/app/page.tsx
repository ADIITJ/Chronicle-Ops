export default function Home() {
    return (
        <main className="min-h-screen">
            {/* Hero Section */}
            <section className="relative overflow-hidden py-20 px-4">
                <div className="absolute inset-0 bg-gradient-to-br from-primary-900/20 via-transparent to-accent-900/20"></div>
                <div className="max-w-6xl mx-auto relative z-10">
                    <div className="text-center animate-fade-in">
                        <h1 className="text-6xl font-bold mb-6">
                            <span className="text-gradient">Time-Locked</span> Multi-Agent
                            <br />
                            Company Simulation
                        </h1>
                        <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
                            Model how your company would operate under realistic constraints, market events,
                            and information asymmetry. Production-grade simulation with deterministic execution
                            and comprehensive auditability.
                        </p>
                        <div className="flex justify-center space-x-4">
                            <a href="/builder" className="btn-primary">
                                Create Simulation
                            </a>
                            <a href="/simulations" className="btn-secondary">
                                View Examples
                            </a>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Grid */}
            <section className="py-20 px-4">
                <div className="max-w-6xl mx-auto">
                    <h2 className="text-4xl font-bold text-center mb-12 text-gradient">
                        Production-Grade Features
                    </h2>
                    <div className="grid md:grid-cols-3 gap-8">
                        <div className="card animate-slide-up">
                            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg mb-4 flex items-center justify-center">
                                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold mb-2">Time-Lock Enforcement</h3>
                            <p className="text-gray-400">
                                Agents cannot access future events. Cryptographically enforced information constraints
                                ensure realistic decision-making.
                            </p>
                        </div>

                        <div className="card animate-slide-up" style={{ animationDelay: '0.1s' }}>
                            <div className="w-12 h-12 bg-gradient-to-br from-accent-500 to-accent-600 rounded-lg mb-4 flex items-center justify-center">
                                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold mb-2">Deterministic Execution</h3>
                            <p className="text-gray-400">
                                Same seed → same outcomes. Reproducible simulations with checkpoint and branching support.
                            </p>
                        </div>

                        <div className="card animate-slide-up" style={{ animationDelay: '0.2s' }}>
                            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg mb-4 flex items-center justify-center">
                                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold mb-2">Audit Trail</h3>
                            <p className="text-gray-400">
                                Tamper-evident ledger of all decisions, state changes, and policy checks with cryptographic signatures.
                            </p>
                        </div>

                        <div className="card animate-slide-up" style={{ animationDelay: '0.3s' }}>
                            <div className="w-12 h-12 bg-gradient-to-br from-primary-600 to-primary-700 rounded-lg mb-4 flex items-center justify-center">
                                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold mb-2">Multi-Agent System</h3>
                            <p className="text-gray-400">
                                CEO, CFO, COO, Product, Sales, and Risk agents with role-specific objectives and permissions.
                            </p>
                        </div>

                        <div className="card animate-slide-up" style={{ animationDelay: '0.4s' }}>
                            <div className="w-12 h-12 bg-gradient-to-br from-accent-600 to-accent-700 rounded-lg mb-4 flex items-center justify-center">
                                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold mb-2">Industry Templates</h3>
                            <p className="text-gray-400">
                                SaaS, D2C, Manufacturing, and Logistics models with realistic operational dynamics.
                            </p>
                        </div>

                        <div className="card animate-slide-up" style={{ animationDelay: '0.5s' }}>
                            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-600 rounded-lg mb-4 flex items-center justify-center">
                                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <h3 className="text-xl font-bold mb-2">Policy Enforcement</h3>
                            <p className="text-gray-400">
                                Guardrails prevent invalid actions. Spend limits, approval thresholds, and risk constraints.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-20 px-4">
                <div className="max-w-4xl mx-auto text-center">
                    <div className="card">
                        <h2 className="text-3xl font-bold mb-4">Ready to Simulate?</h2>
                        <p className="text-gray-300 mb-6">
                            Create your first simulation in minutes. Model realistic business scenarios
                            with time-locked agents and comprehensive audit trails.
                        </p>
                        <a href="/builder" className="btn-primary inline-block">
                            Get Started
                        </a>
                    </div>
                </div>
            </section>
        </main>
    )
}
