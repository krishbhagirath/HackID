export enum Verdict {
    INVALID = 'INVALID',
    LEAN_INVALID = 'LEAN INVALID',
    LEAN_VALID = 'LEAN VALID',
    VALID = 'VALID'
}

export interface ProjectResult {
    id: string;
    hackathon_id?: string;
    name: string;
    submitter: string;
    score: number;
    verdict: Verdict;
    github_link?: string;
}

export interface Hackathon {
    id: string;
    name: string;
    devpost_url: string;
    start_time: string;
    end_time: string;
    project_count: number;
}

export interface Stats {
    totalScanned: number;
    flagged: number;
}
