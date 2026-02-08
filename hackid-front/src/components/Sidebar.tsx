
import React from 'react';
import { Verdict, type Stats } from '../types';

interface SidebarProps {
  url: string;
  setUrl: (url: string) => void;
  onScan: () => void;
  isScanning: boolean;
  activeVerdict: Verdict | 'ALL';
  setActiveVerdict: (v: Verdict | 'ALL') => void;
  minScore: number;
  setMinScore: (s: number) => void;
  stats: Stats;
  view?: 'HACKATHONS' | 'PROJECTS';
}

export default function Sidebar({ 
  url, setUrl, onScan, isScanning, 
  activeVerdict, setActiveVerdict,
  minScore, setMinScore,
  stats,
  view = 'PROJECTS'
}: SidebarProps) {
  return (
    <aside className="w-full lg:w-80 flex-shrink-0">
      <div className="sticky top-32 space-y-6">
        {/* Target URL Box - Only show in Projects view or allow adding new ones */}
        <div className="brutal-border bg-zinc-900 p-6 brutal-shadow">
          <label className="block text-xs font-bold uppercase mb-2">
            {view === 'HACKATHONS' ? 'Import New Hackathon' : 'Scan Specific URL'}
          </label>
          <div className="relative">
            <input 
              className="w-full p-3 brutal-border bg-zinc-900 dark:bg-zinc-800 font-mono text-sm focus:ring-0 focus:outline-none focus:border-primary text-white dark:text-white" 
              type="text" 
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder={view === 'HACKATHONS' ? "enter devpost url" : "enter devpost url"}
            />
          </div>
          <button 
            onClick={onScan}
            disabled={isScanning || !url}
            className="w-full mt-4 bg-primary text-black font-bold py-3 px-6 brutal-border brutal-shadow hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all uppercase disabled:opacity-50"
          >
            {isScanning ? 'Processing...' : (view === 'HACKATHONS' ? 'Scan Hackathon' : 'Scan Devpost')}
          </button>
        </div>

        {/* Filters Box - Only show in Projects view */}
        {view === 'PROJECTS' && (
          <div className="brutal-border bg-zinc-900 p-6 brutal-shadow">
            <h3 className="font-display uppercase text-lg mb-4 border-b-2 border-zinc-200 dark:border-zinc-700 pb-2">Filters</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase mb-2">Verdict Level</label>
                <div className="flex flex-wrap gap-2">
                  {(Object.values(Verdict) as string[]).concat(['ALL']).map((v) => (
                    <button 
                      key={v}
                      onClick={() => setActiveVerdict(v as any)}
                      className={`px-3 py-1 text-[10px] font-bold brutal-border transition-colors ${
                        activeVerdict === v 
                          ? (v === Verdict.INVALID || v === Verdict.LEAN_INVALID ? 'bg-brutal-red text-white' : 'bg-brutal-green text-black')
                          : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'
                      }`}
                    >
                      {v}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-xs font-bold uppercase mb-2">Min. Similarity: {minScore}%</label>
                <input 
                  className="w-full h-2 bg-zinc-200 rounded-none appearance-none cursor-pointer accent-primary" 
                  type="range"
                  min="0"
                  max="100"
                  value={minScore}
                  onChange={(e) => setMinScore(parseInt(e.target.value))}
                />
              </div>
            </div>
          </div>
        )}

        {/* Stats Summary - Only show in Projects view */}
        {view === 'PROJECTS' && (
          <div className="brutal-border bg-zinc-800 p-6">
            <div className="grid grid-cols-2 gap-4 text-white dark:text-white">
              <div>
                <div className="text-3xl font-display font-black">{stats.totalScanned}</div>
                <div className="text-[10px] uppercase font-bold">In View</div>
              </div>
              <div>
                <div className="text-3xl font-display font-black text-brutal-red">{stats.flagged}</div>
                <div className="text-[10px] uppercase font-bold">Flagged</div>
              </div>
            </div>
          </div>
        )}

        {view === 'HACKATHONS' && (
          <div className="brutal-border bg-zinc-800 p-6 text-white">
            <h3 className="font-display uppercase text-lg mb-4 border-b-2 border-zinc-700 pb-2">Overview</h3>
            <p className="text-xs font-bold mb-2">ACTIVE SESSIONS: 1</p>
            <p className="text-xs font-bold mb-2 text-primary">DATABASE: CONNECTED</p>
            <p className="text-xs opacity-60 mt-4 leading-relaxed uppercase">
              Select a hackathon from the list to view detailed plagiarism reports and project metrics.
            </p>
          </div>
        )}
      </div>
    </aside>
  );
}
;

