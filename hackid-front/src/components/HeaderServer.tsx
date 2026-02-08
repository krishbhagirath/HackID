import { Suspense } from "react";
import AuthStatus from "./AuthStatus";

interface HeaderServerProps {
    children?: React.ReactNode;
}

/**
 * Server Header Wrapper
 * Integrates authentication status into the header layout
 */
export default function HeaderServer({ children }: HeaderServerProps) {
    return (
        <header className="border-b-4 border-brutal-black dark:border-white p-6 sticky top-0 bg-background-light dark:bg-background-dark z-50">
            <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
                {/* Logo Section */}
                <div className="flex items-center gap-4">
                    <div className="bg-primary p-3 brutal-border brutal-shadow">
                        <span className="material-icons text-black text-3xl font-bold">security</span>
                    </div>
                    <div>
                        <h1 className="font-display text-2xl md:text-3xl uppercase leading-none">HackCheck_v1.0</h1>
                        <p className="text-xs font-bold opacity-70 uppercase tracking-widest">Plagiarism Detection Engine</p>
                    </div>
                </div>

                {/* Right Section */}
                <div className="flex items-center gap-6">
                    <div className="hidden md:flex flex-col items-end">
                        <span className="text-xs uppercase font-bold">Status: Online</span>
                        <span className="text-xs uppercase font-bold text-brutal-green">Engine: Active</span>
                    </div>

                    {/* Theme toggle passed as children */}
                    {children}

                    {/* Auth Status */}
                    <Suspense fallback={
                        <div className="w-10 h-10 brutal-border bg-zinc-800 animate-pulse" />
                    }>
                        <AuthStatus />
                    </Suspense>
                </div>
            </div>
        </header>
    );
}
