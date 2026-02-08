'use client';

import React from 'react';
import { type Hackathon } from '~/types';

interface HackathonCardProps {
    hackathon: Hackathon;
    onClick: (id: string) => void;
}

export default function HackathonCard({ hackathon, onClick }: HackathonCardProps) {
    const startDate = new Date(hackathon.start_time).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });

    return (
        <div 
            onClick={() => onClick(hackathon.id)}
            className="group brutal-border bg-white dark:bg-zinc-900 p-6 brutal-shadow-hover transition-all cursor-pointer hover:-translate-x-1 hover:-translate-y-1 active:translate-x-0 active:translate-y-0"
        >
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div className="flex-grow">
                    <div className="flex items-center gap-3 mb-2">
                        <span className="bg-primary text-black text-[10px] font-bold px-2 py-0.5 brutal-border-sm uppercase">
                            Hackathon
                        </span>
                        <span className="text-xs font-mono font-bold opacity-50 uppercase">
                            ID: {hackathon.id.slice(0, 8)}
                        </span>
                    </div>
                    <h3 className="text-2xl md:text-3xl font-display font-black uppercase mb-1 group-hover:text-primary transition-colors">
                        {hackathon.name}
                    </h3>
                    <p className="font-mono text-sm opacity-70 mb-4 truncate max-w-xl">
                        {hackathon.devpost_url}
                    </p>
                    
                    <div className="flex flex-wrap gap-4 items-center">
                        <div className="flex items-center gap-2">
                            <span className="material-icons text-sm opacity-50">calendar_today</span>
                            <span className="text-xs font-bold uppercase">{startDate}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="material-icons text-sm opacity-50">inventory_2</span>
                            <span className="text-xs font-bold uppercase">{hackathon.project_count} Projects Scanned</span>
                        </div>
                    </div>
                </div>

                <div className="flex flex-col items-end gap-2 w-full md:w-auto">
                    <div className="bg-black text-white dark:bg-white dark:text-black py-2 px-6 brutal-border font-bold uppercase text-sm w-full md:w-auto text-center group-hover:bg-primary group-hover:text-black transition-colors">
                        View Projects
                    </div>
                </div>
            </div>
        </div>
    );
}
