
import { type ProjectResult, Verdict, AIGenConfidence } from './types';

export const INITIAL_PROJECTS: ProjectResult[] = [
    {
        id: '1',
        name: 'Cyber-Vault-Alpha',
        submitter: '@TEAM_ZERODAY',
        score: 92,
        verdict: Verdict.INVALID,
        matchesFound: 14,
        aiGenConfidence: AIGenConfidence.LOW,
        thumbnail: 'https://picsum.photos/seed/cyber/400/250',
        timestamp: '2023-10-27T14:22:01Z'
    },
    {
        id: '2',
        name: 'Eco-Scan-Node',
        submitter: '@HACKER_BOB',
        score: 45,
        verdict: Verdict.LEAN_VALID,
        matchesFound: 2,
        aiGenConfidence: AIGenConfidence.HIGH,
        thumbnail: 'https://picsum.photos/seed/eco/400/250',
        timestamp: '2023-10-27T14:22:01Z'
    },
    {
        id: '3',
        name: 'Quantum-Chat',
        submitter: '@QUBIT_TEAM',
        score: 12,
        verdict: Verdict.VALID,
        matchesFound: 0,
        aiGenConfidence: AIGenConfidence.NONE,
        thumbnail: 'https://picsum.photos/seed/quantum/400/250',
        timestamp: '2023-10-27T14:22:01Z'
    }
];
