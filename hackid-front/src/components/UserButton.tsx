"use client";

import React, { useState } from "react";
import Image from "next/image";

interface UserButtonProps {
    user: {
        name?: string | null;
        email?: string | null;
        picture?: string | null;
    } | null;
    isVerified: boolean;
    role: string;
}

export default function UserButton({ user, isVerified, role }: UserButtonProps) {
    const [isOpen, setIsOpen] = useState(false);

    if (!user) {
        return (
            <a
                href="/auth/login"
                className="bg-primary text-black font-bold py-2 px-6 brutal-border brutal-shadow hover:shadow-none hover:translate-x-1 hover:translate-y-1 transition-all uppercase text-sm"
            >
                Login
            </a>
        );
    }

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-3 bg-zinc-800 brutal-border px-3 py-2 hover:bg-zinc-700 transition-colors"
            >
                {user.picture ? (
                    <Image
                        src={user.picture}
                        alt={user.name ?? "User"}
                        width={32}
                        height={32}
                        className="w-8 h-8 rounded-full border-2 border-white"
                    />
                ) : (
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-black font-bold">
                        {user.name?.charAt(0) ?? "U"}
                    </div>
                )}
                <div className="text-left hidden sm:block">
                    <div className="text-sm font-bold truncate max-w-[120px]">
                        {user.name ?? (user.email ?? "User")}
                    </div>
                    <div className={`text-xs uppercase ${isVerified ? "text-green-400" : "text-red-400"}`}>
                        {role}
                    </div>
                </div>
                <span className="material-icons text-sm">
                    {isOpen ? "expand_less" : "expand_more"}
                </span>
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-zinc-900 brutal-border brutal-shadow z-50">
                    <div className="p-3 border-b-2 border-black">
                        <div className="text-sm font-bold truncate">{user.email}</div>
                        <div className={`text-xs uppercase mt-1 ${isVerified ? "text-green-400" : "text-red-400"}`}>
                            {isVerified ? "✓ Verified" : "✗ Unverified"}
                        </div>
                    </div>
                    <a
                        href="/dashboard"
                        className="block px-3 py-2 text-sm hover:bg-zinc-800 transition-colors"
                    >
                        <span className="material-icons text-sm mr-2 align-middle">dashboard</span>
                        Dashboard
                    </a>
                    <a
                        href="/auth/logout"
                        className="block px-3 py-2 text-sm hover:bg-zinc-800 transition-colors text-red-400"
                    >
                        <span className="material-icons text-sm mr-2 align-middle">logout</span>
                        Logout
                    </a>
                </div>
            )}
        </div>
    );
}
