'use client';

import React from 'react';

interface UserButtonProps {
    user: {
        name?: string;
        email?: string;
        picture?: string;
    } | null;
    isVerified?: boolean;
    roleName?: string;
}

export default function UserButton({ user, isVerified, roleName }: UserButtonProps) {
    if (!user) {
        return (
            <a
                href="/auth/login"
                className="brutal-border px-4 py-2 bg-primary text-black font-bold text-sm uppercase hover:bg-yellow-400 transition-colors brutal-shadow hover:shadow-none hover:translate-x-1 hover:translate-y-1"
            >
                Login
            </a>
        );
    }

    return (
        <div className="flex items-center gap-3">
            {/* User Info */}
            <div className="hidden md:flex flex-col items-end">
                <span className="text-xs uppercase font-bold truncate max-w-[150px]">
                    {user.name || user.email}
                </span>
                <span className={`text-xs uppercase font-bold ${isVerified ? 'text-brutal-green' : 'text-brutal-red'}`}>
                    {roleName || (isVerified ? 'Verified' : 'Guest')}
                </span>
            </div>

            {/* Avatar */}
            <div className="relative group">
                <div className="w-10 h-10 brutal-border overflow-hidden bg-zinc-800">
                    {user.picture ? (
                        <img
                            src={user.picture}
                            alt={user.name || 'User'}
                            className="w-full h-full object-cover"
                        />
                    ) : (
                        <div className="w-full h-full flex items-center justify-center bg-primary text-black font-bold">
                            {(user.name || user.email || 'U')[0]?.toUpperCase()}
                        </div>
                    )}
                </div>

                {/* Dropdown Menu */}
                <div className="absolute right-0 top-full mt-2 w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                    <div className="brutal-border bg-zinc-900 brutal-shadow">
                        <div className="p-3 border-b-2 border-white/20">
                            <p className="text-xs font-bold uppercase truncate">{user.email}</p>
                            <p className={`text-xs mt-1 ${isVerified ? 'text-brutal-green' : 'text-brutal-red'}`}>
                                {isVerified ? '✓ VERIFIED ORGANIZER' : '✗ NOT VERIFIED'}
                            </p>
                        </div>

                        {isVerified && (
                            <a
                                href="/dashboard"
                                className="block px-3 py-2 text-xs font-bold uppercase hover:bg-primary hover:text-black transition-colors"
                            >
                                Dashboard
                            </a>
                        )}

                        <a
                            href="/auth/logout"
                            className="block px-3 py-2 text-xs font-bold uppercase text-brutal-red hover:bg-brutal-red hover:text-white transition-colors"
                        >
                            Logout
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
}
