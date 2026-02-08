import { Suspense } from "react";
import AuthStatus from "./AuthStatus";

interface HeaderServerProps {
    isDark: boolean;
    toggleTheme: () => void;
}

function HeaderSkeleton() {
    return (
        <div className="bg-zinc-800 brutal-border px-3 py-2 animate-pulse">
            <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-zinc-700" />
                <div className="hidden sm:block">
                    <div className="h-4 w-24 bg-zinc-700 rounded mb-1" />
                    <div className="h-3 w-16 bg-zinc-700 rounded" />
                </div>
            </div>
        </div>
    );
}

export default function HeaderServer({ isDark, toggleTheme }: HeaderServerProps) {
    return (
        <header className="brutal-border bg-zinc-900 p-4 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-6">
                <h1 className="font-display text-3xl md:text-4xl font-black uppercase italic tracking-tighter text-white">
                    HACKCHECK<span className="text-primary">_</span>
                </h1>
                <div className="hidden md:flex items-center gap-2 bg-green-500/20 border-2 border-green-500 px-3 py-1">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-green-400 font-bold text-xs uppercase">System Online</span>
                </div>
            </div>

            <div className="flex items-center gap-4">
                <button
                    onClick={toggleTheme}
                    className="brutal-border p-2 hover:bg-zinc-800 transition-colors"
                    aria-label="Toggle theme"
                >
                    <span className="material-icons">
                        {isDark ? "light_mode" : "dark_mode"}
                    </span>
                </button>

                <Suspense fallback={<HeaderSkeleton />}>
                    <AuthStatus />
                </Suspense>
            </div>
        </header>
    );
}
