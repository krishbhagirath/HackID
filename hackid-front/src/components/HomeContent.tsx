'use client';

import React, { useState, useMemo, useEffect } from 'react';
import Header from '~/components/Header';
import Sidebar from '~/components/Sidebar';
import ProjectCard from '~/components/ProjectCard';
import HackathonCard from '~/components/HackathonCard';
import { type ProjectResult, Verdict, type Stats, type Hackathon } from '~/types';
import { INITIAL_PROJECTS, INITIAL_HACKATHONS } from '~/constants';
import { getHackathons, getProjectsByHackathon, scanUrl } from '~/app/actions';
import { useRouter } from 'next/navigation';

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
    
    const [view, setView] = useState<'HACKATHONS' | 'PROJECTS'>('HACKATHONS');
    const [limit, setLimit] = useState(10);
    const router = useRouter();
    const [hackathons, setHackathons] = useState<Hackathon[]>(INITIAL_HACKATHONS);
    const [selectedHackathon, setSelectedHackathon] = useState<Hackathon | null>(null);
    const [projects, setProjects] = useState<ProjectResult[]>([]);
    
    const [activeVerdict, setActiveVerdict] = useState<Verdict | 'ALL'>('ALL');
    const [searchQuery, setSearchQuery] = useState('');

    // Initial fetch of hackathons
    useEffect(() => {
        const fetchHackathons = async () => {
            const data = await getHackathons();
            if (data.length > 0) {
                setHackathons(data);
            }
        };
        fetchHackathons();
    }, []);

    const toggleTheme = () => {
        setIsDark(prev => !prev);
    };

    const handleHackathonClick = async (hackathonId: string) => {
        const hackathon = hackathons.find(h => h.id === hackathonId);
        if (!hackathon) return;

        setSelectedHackathon(hackathon);
        setIsScanning(true);
        
        // Fetch projects for this hackathon
        const projectsData = await getProjectsByHackathon(hackathonId);
        if (projectsData.length > 0) {
            setProjects(projectsData);
        } else {
            // Fallback to initial projects if DB is empty for this hackathon
            setProjects(INITIAL_PROJECTS.filter(p => p.hackathon_id === hackathonId));
        }
        
        setIsScanning(false);
        setView('PROJECTS');
        // Reset filters when changing hackathon
        setActiveVerdict('ALL');
        setSearchQuery('');
    };

    const handleBackToHackathons = () => {
        setView('HACKATHONS');
        setSelectedHackathon(null);
        setProjects([]);
    };

    const handleScan = async () => {
        if (!url) return;
        setIsScanning(true);
        
        try {
            const result = await scanUrl(url, limit);
            if (result.success) {
                // Refresh data based on current view
                if (view === 'HACKATHONS') {
                    const data = await getHackathons();
                    if (data.length > 0) setHackathons(data);
                } else if (selectedHackathon) {
                    const data = await getProjectsByHackathon(selectedHackathon.id);
                    if (data.length > 0) setProjects(data);
                }
                
                // Refresh server components
                router.refresh();
            } else {
                alert(`Scan failed: ${result.message}`);
            }
        } catch (error) {
            console.error("Scan error:", error);
        } finally {
            setIsScanning(false);
        }
    };

    const handleClear = () => {
        setProjects([]);
    };

    const filteredProjects = useMemo(() => {
        return projects.filter(p => {
            const matchVerdict = activeVerdict === 'ALL' || p.verdict === activeVerdict;
            const matchSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase());
            return matchVerdict && matchSearch;
        });
    }, [projects, activeVerdict, searchQuery]);

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
                    searchQuery={searchQuery}
                    setSearchQuery={setSearchQuery}
                    stats={stats}
                    view={view}
                    limit={limit}
                    setLimit={setLimit}
                />

                <section className="flex-grow">
                    <div className="flex flex-col md:flex-row justify-between items-end mb-8 gap-4">
                        <div>
                            {view === 'PROJECTS' && selectedHackathon && (
                                <button 
                                    onClick={handleBackToHackathons}
                                    className="flex items-center gap-2 text-primary font-bold uppercase text-xs mb-4 hover:underline"
                                >
                                    <span className="material-icons text-sm">arrow_back</span>
                                    Back to Hackathons
                                </button>
                            )}
                            <h2 className="font-display text-5xl md:text-6xl uppercase leading-none mb-2 italic">
                                {view === 'HACKATHONS' ? 'Hackathons' : 'Projects'}
                            </h2>
                            <div className="flex items-center gap-4">
                                <p className="font-bold opacity-60 uppercase text-sm tracking-tighter">
                                    {view === 'HACKATHONS' ? 'Scanned Hackathons' : `Results for ${selectedHackathon?.name}`}
                                </p>
                                {view === 'PROJECTS' && (
                                    <button
                                        onClick={handleClear}
                                        className="text-[10px] font-bold uppercase border-b border-brutal-red text-brutal-red hover:bg-brutal-red hover:text-white px-1"
                                    >
                                        Clear Results
                                    </button>
                                )}
                            </div>
                        </div>
                        <div className="bg-black text-white dark:bg-white dark:text-black px-4 py-2 font-bold text-sm brutal-shadow">
                            {view === 'HACKATHONS' 
                                ? `DISPLAYING ${hackathons.length} HACKATHONS` 
                                : `DISPLAYING ${filteredProjects.length} / ${projects.length} PROJECTS`}
                        </div>
                    </div>

                    <div className="space-y-8">
                        {view === 'HACKATHONS' ? (
                            hackathons.map(hackathon => (
                                <HackathonCard 
                                    key={hackathon.id} 
                                    hackathon={hackathon} 
                                    onClick={handleHackathonClick} 
                                />
                            ))
                        ) : (
                            filteredProjects.map(project => (
                                <ProjectCard key={project.id} project={project} />
                            ))
                        )}

                        {((view === 'PROJECTS' && (filteredProjects.length === 0 || projects.length === 0)) || 
                          (view === 'HACKATHONS' && hackathons.length === 0)) && (
                            <div className="text-center py-24 brutal-border bg-zinc-900/50 dark:bg-zinc-900 brutal-shadow-hover transition-all">
                                <span className="material-icons text-6xl mb-4 text-zinc-300">inventory_2</span>
                                <h3 className="text-2xl font-display uppercase font-black">
                                    {view === 'HACKATHONS' ? 'No hackathons found' : 'No projects found'}
                                </h3>
                                <p className="font-bold uppercase opacity-50 text-sm mt-2">
                                    The database returned zero results.
                                </p>
                            </div>
                        )}
                    </div>
                </section>
            </main>

            <footer className="mt-20 border-t-4 border-brutal-black dark:border-white p-8 bg-zinc-900 text-white dark:text-white">
                <div className="max-w-[1400px] mx-auto">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-6">
                        <div className="font-mono text-xs">
                            <p>&gt; FOUNDER 1: KARL ANDRES</p>
                            <p>&gt; FOUNDER 2: KRISH BHAGIRATH</p>
                            <p>&gt; FOUNDER 3: KAJURAN ELANGANATHAN</p>
                        </div>
                        <div className="flex gap-8 uppercase font-bold text-sm">
                            <a className="hover:underline" href="#">git</a>
                            <a className="hover:underline" href="#">it</a>
                            <a className="hover:underline" href="#">in</a>
                        </div>
                        <div className="font-display font-black text-2xl italic">
                            .gitcheck
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}
