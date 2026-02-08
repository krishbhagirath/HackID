import React from 'react';
import { type ProjectResult, Verdict } from '../types';

interface ProjectCardProps {
  project: ProjectResult;
}

export default function ProjectCard({ project }: ProjectCardProps) {
  const getVerdictColor = (v: Verdict) => {
    switch(v) {
      case Verdict.INVALID: return 'text-brutal-red';
      case Verdict.LEAN_INVALID: return 'text-orange-500';
      case Verdict.LEAN_VALID: return 'text-zinc-400';
      case Verdict.VALID: return 'text-brutal-green';
      default: return '';
    }
  };

  const isHighSimilarity = project.score > 80;

  return (
    <div className="group brutal-border bg-zinc-900 brutal-shadow brutal-shadow-hover transition-all relative overflow-hidden text-white dark:text-white">
      {isHighSimilarity && (
        <div className="absolute top-0 right-0 bg-brutal-red text-white font-bold px-4 py-1 text-xs uppercase z-10">
          High Similarity Alert
        </div>
      )}
      <div className="p-6 md:p-8 flex flex-col gap-6">
        <div>
          <h3 className="text-2xl font-display uppercase leading-none mb-1">Project: {project.name}</h3>
          <p className="text-sm font-bold opacity-50 uppercase tracking-tighter">SUBMITTED BY: {project.submitter}</p>
        </div>

        {/* change "#" to however many fields we have grid-cols-#  */}
        <div className="grid grid-cols-2 gap-4">
          {/* field 1 */}
          <div className="p-4 border-2 border-zinc-900 dark:border-zinc-800 brutal-border bg-zinc-800 dark:bg-zinc-800/50">
            <span className="block text-xs font-bold uppercase mb-2 opacity-60">Similarity Score</span>
            <span className={`text-3xl font-display font-black ${project.score > 70 ? 'text-brutal-red' : project.score > 40 ? 'text-primary' : 'text-brutal-green'}`}>
              {project.score}%
            </span>
          </div>
          {/* field 2 */}
          <div className="p-4 border-2 border-zinc-900 dark:border-zinc-800 brutal-border bg-zinc-800 dark:bg-zinc-800/50">
            <span className="block text-xs font-bold uppercase mb-2 opacity-60">System Verdict</span>
            <span className={`text-3xl font-display font-black uppercase ${getVerdictColor(project.verdict)}`}>
              {project.verdict}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap gap-4 pt-2">
          <button className="bg-black text-white dark:bg-white dark:text-black font-bold py-3 px-8 uppercase text-sm hover:bg-primary hover:text-black transition-all brutal-shadow active:translate-x-1 active:translate-y-1 active:shadow-none">
            Detailed Analysis
          </button>
          {project.github_link && (
            <a 
              href={project.github_link}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-zinc-800 text-white font-bold py-3 px-8 uppercase text-sm brutal-border hover:bg-zinc-700 transition-colors flex items-center gap-2"
            >
              <span className="material-icons text-sm">code</span>
              GitHub Source
            </a>
          )}
          <button className="brutal-border font-bold py-3 px-8 uppercase text-sm hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors">
            View Source
          </button>
        </div>
      </div>
    </div>
  );
};