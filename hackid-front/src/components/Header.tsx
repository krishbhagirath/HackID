'use client';

import React from 'react';

interface HeaderProps {
  isDark: boolean;
  toggleTheme: () => void;
  user?: {
    name?: string | null;
    email?: string | null;
    picture?: string | null;
  } | null;
}

export default function Header({ isDark, toggleTheme, user }: HeaderProps) {
  return (
    <header className="border-b-4 border-brutal-black dark:border-white p-6 sticky top-0 bg-background-light dark:bg-background-dark z-50">
      <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex items-center gap-4">
          <div className="bg-primary p-3 brutal-border brutal-shadow">
            <span className="material-icons text-black text-3xl font-bold">security</span>
          </div>
          <div>
            <h1 className="font-display text-2xl md:text-3xl uppercase leading-none">.gitcheck_v1.0</h1>
            <p className="text-xs font-bold opacity-70 uppercase tracking-widest">Turnitin for Hackathons</p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="hidden md:flex flex-col items-end">
            <span className="text-xs uppercase font-bold">Status: Online</span>
            <span className="text-xs uppercase font-bold text-brutal-green">Engine: Active</span>
          </div>
          <button
            onClick={toggleTheme}
            className="brutal-border p-2 bg-zinc-900 dark:bg-brutal-black hover:bg-primary hover:text-black transition-colors"
            aria-label="Toggle theme"
          >
            <span className="material-icons">{isDark ? 'light_mode' : 'dark_mode'}</span>
          </button>

          {/* Auth Button */}
          {user ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 bg-zinc-800 brutal-border px-3 py-2">
                {user.picture ? (
                  <img
                    src={user.picture}
                    alt={user.name || "User"}
                    className="w-8 h-8 rounded-full border-2 border-primary"
                  />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-black font-bold">
                    {user.name?.charAt(0) || "U"}
                  </div>
                )}
                <span className="text-sm font-bold hidden sm:block">{user.name || user.email}</span>
              </div>
              <a
                href="/auth/logout"
                className="brutal-border p-2 bg-red-600 hover:bg-red-500 transition-colors text-white"
                title="Logout"
              >
                <span className="material-icons">logout</span>
              </a>
            </div>
          ) : (
            <a
              href="/auth/login"
              className="bg-primary text-black font-bold py-2 px-6 brutal-border brutal-shadow hover:shadow-none hover:translate-x-1 hover:translate-y-1 transition-all uppercase text-sm"
            >
              Login
            </a>
          )}
        </div>
      </div>
    </header>
  );
};

