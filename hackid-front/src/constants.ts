
import { type ProjectResult, type Hackathon, Verdict } from './types';

export const INITIAL_HACKATHONS: Hackathon[] = [
    {
        id: 'h1',
        name: 'ETHGlobal London 2024',
        devpost_url: 'https://ethglobal-london.devpost.com',
        start_time: '2024-03-15T09:00:00Z',
        end_time: '2024-03-17T17:00:00Z',
        project_count: 3
    },
    {
        id: 'h2',
        name: 'Build with AI Hackathon',
        devpost_url: 'https://build-with-ai.devpost.com',
        start_time: '2024-04-10T09:00:00Z',
        end_time: '2024-04-12T17:00:00Z',
        project_count: 1
    }
];

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
