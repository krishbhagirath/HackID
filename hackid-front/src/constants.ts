
import { type ProjectResult, Verdict } from './types';

export const INITIAL_PROJECTS: ProjectResult[] = [
    {
        id: '1',
        name: 'Cyber-Vault-Alpha',
        submitter: '@TEAM_ZERODAY',
        score: 92,
        verdict: Verdict.INVALID,
    },
    {
        id: '2',
        name: 'Eco-Scan-Node',
        submitter: '@HACKER_BOB',
        score: 45,
        verdict: Verdict.LEAN_VALID,
    },
    {
        id: '3',
        name: 'Quantum-Chat',
        submitter: '@QUBIT_TEAM',
        score: 12,
        verdict: Verdict.VALID,
    }
];
