
import { type ProjectResult, type Hackathon, Verdict } from './types';

// No longer using dummy data - load from database
export const INITIAL_HACKATHONS: Hackathon[] = [];

export const INITIAL_PROJECTS: ProjectResult[] = [
    {
        id: '1',
        hackathon_id: 'h1',
        name: 'Cyber-Vault-Alpha',
        submitter: '@TEAM_ZERODAY',
        score: 92,
        verdict: Verdict.INVALID,
        github_link: 'https://github.com/team-zeroday/vault'
    },
    {
        id: '2',
        hackathon_id: 'h1',
        name: 'Eco-Scan-Node',
        submitter: '@HACKER_BOB',
        score: 45,
        verdict: Verdict.LEAN_VALID,
        github_link: 'https://github.com/hacker-bob/eco-scan'
    },
    {
        id: '3',
        hackathon_id: 'h1',
        name: 'Quantum-Chat',
        submitter: '@QUBIT_TEAM',
        score: 12,
        verdict: Verdict.VALID,
        github_link: 'https://github.com/qubit-team/qchat'
    },
    {
        id: '4',
        hackathon_id: 'h2',
        name: 'AI-Logistics-Optimizer',
        submitter: '@LOGI_GENIUS',
        score: 30,
        verdict: Verdict.VALID,
        github_link: 'https://github.com/logi-genius/optimizer'
    }
];
