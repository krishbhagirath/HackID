export enum Verdict {
    INVALID = 'INVALID',
    LEAN_INVALID = 'LEAN INVALID',
    LEAN_VALID = 'LEAN VALID',
    VALID = 'VALID'
}

export interface ProjectResult {
    id: string;
    name: string;
    submitter: string;
    score: number;
    verdict: Verdict;
}

export interface Stats {
    totalScanned: number;
    flagged: number;
}
