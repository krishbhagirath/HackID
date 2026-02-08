'use client';

import React, { useState, useMemo } from 'react';
import Header from '~/components/Header';
import Sidebar from '~/components/Sidebar';
import ProjectCard from '~/components/ProjectCard';
import { type ProjectResult, Verdict, type Stats } from '~/types';
import { INITIAL_PROJECTS } from '~/constants';

interface HomeContentProps {
    user?: {
        name?: string | null;
        email?: string | null;
        picture?: string | null;
    } | null;
}

export default function HomeContent({ user }: HomeContentProps) {
    const [isDark, setIsDark] = useState(true);
    const [url, setUrl] = useState('');
    const [isScanning, setIsScanning] = useState(false);
    const [projects, setProjects] = useState<ProjectResult[]>(INITIAL_PROJECTS);
    const [activeVerdict, setActiveVerdict] = useState<Verdict | 'ALL'>('ALL');
    const [minScore, setMinScore] = useState(0);

    const toggleTheme = () => {
        setIsDark(prev => !prev);
    };

    const handleScan = () => {
        if (!url) return;
        setIsScanning(true);
        setTimeout(() => {
            setProjects(INITIAL_PROJECTS);
            setIsScanning(false);
        }, 800);
    };

    const handleClear = () => {
        setProjects([]);
    };

    const filteredProjects = useMemo(() => {
        return projects.filter(p => {
            const matchVerdict = activeVerdict === 'ALL' || p.verdict === activeVerdict;
            const matchScore = p.score >= minScore;
            return matchVerdict && matchScore;
        });
    }, [projects, activeVerdict, minScore]);

    const stats: Stats = useMemo(() => {
        return {
            totalScanned: projects.length,
            flagged: projects.filter(p => p.verdict === Verdict.INVALID || p.verdict === Verdict.LEAN_INVALID).length
        };
    }, [projects]);

    return (
        <div className={`min-h-screen ${isDark ? 'dark' : ''}`}>
            <Header isDark={isDark} toggleTheme={toggleTheme} user={user} />

            <main className="max-w-[1400px] mx-auto p-6 flex flex-col lg:flex-row gap-8">
                <Sidebar
                    url={url}
                    setUrl={setUrl}
                    onScan={handleScan}
                    isScanning={isScanning}
                    activeVerdict={activeVerdict}
                    setActiveVerdict={setActiveVerdict}
                    minScore={minScore}
                    setMinScore={setMinScore}
                    stats={stats}
                />

                <section className="flex-grow">
                    <div className="flex flex-col md:flex-row justify-between items-end mb-8 gap-4">
                        <div>
                            <h2 className="font-display text-5xl md:text-6xl uppercase leading-none mb-2 italic">Results</h2>
                            <div className="flex items-center gap-4">
                                <p className="font-bold opacity-60 uppercase text-sm tracking-tighter">
                                    Local Database Scan
                                </p>
                                <button
                                    onClick={handleClear}
                                    className="text-[10px] font-bold uppercase border-b border-brutal-red text-brutal-red hover:bg-brutal-red hover:text-white px-1"
                                >
                                    Clear Results
                                </button>
                            </div>
                        </div>
                        <div className="bg-black text-white dark:bg-white dark:text-black px-4 py-2 font-bold text-sm brutal-shadow">
                            DISPLAYING {filteredProjects.length} / {projects.length} ENTRIES
                        </div>
                    </div>

                    <div className="space-y-8">
                        {filteredProjects.map(project => (
                            <ProjectCard key={project.id} project={project} />
                        ))}

                        {(filteredProjects.length === 0 || projects.length === 0) && (
                            <div className="text-center py-24 brutal-border bg-zinc-900/50 dark:bg-zinc-900 brutal-shadow-hover transition-all">
                                <span className="material-icons text-6xl mb-4 text-zinc-300">inventory_2</span>
                                <h3 className="text-2xl font-display uppercase font-black">No projects found</h3>
                                <p className="font-bold uppercase opacity-50 text-sm mt-2">The scanner returned zero results for this directory.</p>
                                {projects.length === 0 && (
                                    <button
                                        onClick={handleScan}
                                        className="mt-6 bg-primary text-black font-bold py-2 px-8 brutal-border brutal-shadow hover:shadow-none hover:translate-x-1 hover:translate-y-1 transition-all uppercase"
                                    >
                                        Load Initial Database
                                    </button>
                                )}
                            </div>
                        )}
                    </div>
                </section>
            </main>

            <footer className="mt-20 border-t-4 border-brutal-black dark:border-white p-8 bg-zinc-900 text-white dark:text-white">
                <div className="max-w-[1400px] mx-auto">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-6">
                        <div className="font-mono text-xs">
                            <p>&gt; SOURCE: CONSTANTS.TS</p>
                            <p>&gt; MODE: STATIC_READONLY</p>
                            <p>&gt; ENGINE: LOCAL_PARSER_V1</p>
                        </div>
                        <div className="flex gap-8 uppercase font-bold text-sm">
                            <a className="hover:underline" href="#">Documentation</a>
                            <a className="hover:underline" href="#">Config Guide</a>
                            <a className="hover:underline" href="#">System Logs</a>
                        </div>
                        <div className="font-display font-black text-2xl italic">
                            HACKCHECK_STATIC
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}
