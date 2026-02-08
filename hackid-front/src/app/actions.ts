'use server';

import { db } from "~/server/db";
import { type Hackathon, type ProjectResult, Verdict } from "~/types";

export async function getHackathons(): Promise<Hackathon[]> {
    try {
        const hackathons = await db.hackathons.findMany({
            include: {
                _count: {
                    select: { projects: true }
                }
            },
            orderBy: {
                start_time: 'desc'
            }
        });

        return hackathons.map((h: any) => ({
            id: h.hackathon_id,
            name: h.name,
            devpost_url: h.devpost_url,
            start_time: h.start_time.toISOString(),
            end_time: h.end_time.toISOString(),
            project_count: h._count.projects
        }));
    } catch (error) {
        console.error("Failed to fetch hackathons:", error);
        return [];
    }
}

export async function getProjectsByHackathon(hackathonId: string): Promise<ProjectResult[]> {
    try {
        const projects = await db.projects.findMany({
            where: {
                hackathon_id: hackathonId
            },
            orderBy: {
                created_at: 'desc'
            }
        });

        return projects.map((p: any) => ({
            id: p.project_id,
            hackathon_id: p.hackathon_id,
            name: p.title || 'Untitled Project',
            submitter: (p.data as any)?.findings?.team?.matched?.[0] || 'Unknown Submitter',
            score: (p.data as any)?.score || 0,
            verdict: (p.data as any)?.status || "UNKNOWN",
            github_link: p.github_repo_link || undefined,
            description: (p.data as any)?.description || undefined
        }));
    } catch (error) {
        console.error("Failed to fetch projects:", error);
        return [];
    }
}

export async function scanUrl(url: string, limit: number): Promise<{ success: boolean; message: string }> {
    try {
        // This is a server action that performs a POST request to your external API
        // You can modify the request body here as requested
        const response = await fetch('YOUR_API_ENDPOINT_HERE', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                hackathon_url: url,
                max_projects: limit,
            }),
        });

        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }

        return { success: true, message: "Scan started successfully" };
    } catch (error) {
        console.error("Scanning failed:", error);
        return { success: false, message: error instanceof Error ? error.message : "Unknown error occurred" };
    }
}
