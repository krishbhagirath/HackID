'use client';

import React from 'react';

interface HeaderProps {
  isDark: boolean;
  toggleTheme: () => void;
}

export default function Header({ isDark, toggleTheme }: HeaderProps) {
  return (
    <header className="border-b-4 border-brutal-black dark:border-white p-6 sticky top-0 bg-background-light dark:bg-background-dark z-50">
      <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex items-center gap-4">
          <div className="bg-primary p-3 brutal-border brutal-shadow">
            <span className="material-icons text-black text-3xl font-bold">security</span>
          </div>
          <div>
            <h1 className="font-display text-2xl md:text-3xl uppercase leading-none">HackCheck_v1.0</h1>
            <p className="text-xs font-bold opacity-70 uppercase tracking-widest">Plagiarism Detection Engine</p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="hidden md:flex flex-col items-end">
            <span className="text-xs uppercase font-bold">Status: Online</span>
            <span className="text-xs uppercase font-bold text-brutal-green">Engine: Active</span>
          </div>
          <button 
            onClick={toggleTheme}
            className="brutal-border p-2 bg-zinc-900 dark:bg-brutal-black hover:bg-primary transition-colors"
            aria-label="Toggle theme"
          >
            {/* <span className="material-icons block dark:hidden">dark_mode</span>
            <span className="material-icons hidden dark:block text-white">light_mode</span> */}
            HACKCHECK
          </button>
        </div>
      </div>
    </header>
  );
};
