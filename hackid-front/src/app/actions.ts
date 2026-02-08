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
            submitter: (p.data as any)?.submitter || 'Unknown Submitter',
            score: (p.data as any)?.score || 0,
            verdict: ((p.data as any)?.verdict as Verdict) || Verdict.VALID,
            github_link: p.github_repo_link || undefined
        }));
    } catch (error) {
        console.error("Failed to fetch projects:", error);
        return [];
    }
}
