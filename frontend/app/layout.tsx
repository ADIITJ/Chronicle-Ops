import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'ChronicleOps - Multi-Agent Company Simulation',
    description: 'Time-locked multi-agent company simulation platform for modeling realistic business operations under constraints',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <nav className="glass-dark border-b border-white/10 sticky top-0 z-50">
                    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div className="flex justify-between h-16 items-center">
                            <div className="flex items-center space-x-2">
                                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg"></div>
                                <span className="text-xl font-bold text-gradient">ChronicleOps</span>
                            </div>
                            <div className="flex space-x-6">
                                <a href="/" className="text-gray-300 hover:text-white transition-colors">Home</a>
                                <a href="/builder" className="text-gray-300 hover:text-white transition-colors">Builder</a>
                                <a href="/simulations" className="text-gray-300 hover:text-white transition-colors">Simulations</a>
                            </div>
                        </div>
                    </div>
                </nav>
                {children}
            </body>
        </html>
    )
}
