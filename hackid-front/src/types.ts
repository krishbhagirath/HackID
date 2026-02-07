export enum Verdict {
    INVALID = 'INVALID',
    LEAN_INVALID = 'LEAN INVALID',
    LEAN_VALID = 'LEAN VALID',
    VALID = 'VALID'
}

export enum AIGenConfidence {
    NONE = 'None',
    LOW = 'Low',
    MEDIUM = 'Medium',
    HIGH = 'High'
}

export interface ProjectResult {
    id: string;
    name: string;
    submitter: string;
    score: number;
    verdict: Verdict;
    matchesFound: number;
    aiGenConfidence: AIGenConfidence;
    thumbnail: string;
    timestamp: string;
}

export interface Stats {
    totalScanned: number;
    flagged: number;
}
