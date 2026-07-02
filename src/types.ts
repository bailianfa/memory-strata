/**
 * Types for Pi Memory Strata extension
 */

export interface MemoryVault {
  root: string;
  brain: string;
  journal: string;
  projects: string;
  knowledge: string;
  learnings: string;
  templates: string;
  scripts: string;
}

export interface MaintenanceReport {
  date: string;
  health: {
    journalCoverage: 'ok' | 'warn';
    devStatus: 'ok' | 'warn';
    coreArchive: 'ok' | 'warn';
    memoryDecay: 'ok' | 'warn';
    anchorIntegrity: 'ok' | 'warn';
    bidirectionalLinks: 'ok' | 'warn';
  };
  issues: string[];
  suggestions: string[];
  archivedCount: number;
  summaryPath?: string;
}

export interface ProjectInfo {
  name: string;
  statusPath: string;
  corePath: string;
  lastStatusUpdate?: string;
  lastCoreUpdate?: string;
  daysSinceStatusUpdate?: number;
  daysSinceCoreUpdate?: number;
  bidirectionalLinks: boolean;
}

export interface DistillCheckResult {
  ok: boolean;
  projects: ProjectInfo[];
  journalMissingDays: string[];
  staleEntries: string[];
  missingAnchors: string[];
}

export interface MemoryConfig {
  vaultPath: string;
  autoArchiveDays: number;
  staleWarningDays: number;
  journalCheckDays: number;
}
