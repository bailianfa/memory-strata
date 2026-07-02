import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { resolve } from 'path';
import type { MemoryConfig, MaintenanceReport, DistillCheckResult, ProjectInfo } from './types.js';

export class MemoryStrata {
  private config: MemoryConfig;
  private vaultPath: string;

  constructor(config?: Partial<MemoryConfig>) {
    this.config = {
      vaultPath: process.env.OBSIDIAN_VAULT_PATH || '',
      autoArchiveDays: 30,
      staleWarningDays: 14,
      journalCheckDays: 7,
      ...config,
    };
    this.vaultPath = this.config.vaultPath;
  }

  /**
   * Run the Python distillation check script
   */
  async check(): Promise<DistillCheckResult> {
    const scriptPath = resolve(import.meta.dirname, '../scripts/memory_distill_check.py');
    if (!existsSync(scriptPath)) {
      throw new Error(`Script not found: ${scriptPath}`);
    }

    const result = execSync(
      `python "${scriptPath}" --vault "${this.vaultPath}"`,
      { encoding: 'utf-8', cwd: this.vaultPath }
    );

    return this.parseCheckOutput(result);
  }

  /**
   * Run the daily maintenance routine
   */
  async maintain(): Promise<MaintenanceReport> {
    const scriptPath = resolve(import.meta.dirname, '../scripts/daily_memory_maintenance.py');
    if (!existsSync(scriptPath)) {
      throw new Error(`Maintenance script not found: ${scriptPath}`);
    }

    const result = execSync(
      `python "${scriptPath}" --vault "${this.vaultPath}"`,
      { encoding: 'utf-8', cwd: this.vaultPath }
    );

    return this.parseMaintenanceOutput(result);
  }

  /**
   * Initialize a new project in the vault
   */
  initProject(projectName: string): void {
    const projectDir = resolve(this.vaultPath, '20-projects', projectName);
    if (existsSync(projectDir)) {
      throw new Error(`Project already exists: ${projectName}`);
    }

    // Copy templates
    const templatesDir = resolve(import.meta.dirname, '../templates');
    execSync(
      `mkdir -p "${projectDir}" && cp "${templatesDir}/01-status.md" "${projectDir}/dev-status.md" && cp "${templatesDir}/02-core.md" "${projectDir}/project-core.md"`,
      { encoding: 'utf-8' }
    );
  }

  private parseCheckOutput(output: string): DistillCheckResult {
    // Parse the output of memory_distill_check.py
    // This is a simplified parser - the actual implementation would parse the full output
    return {
      ok: !output.includes('MISSING') && !output.includes('STALE'),
      projects: [],
      journalMissingDays: [],
      staleEntries: [],
      missingAnchors: [],
    };
  }

  private parseMaintenanceOutput(output: string): MaintenanceReport {
    // Parse the output of daily_memory_maintenance.py
    const health: MaintenanceReport['health'] = {
      journalCoverage: output.includes('L4 journal') && output.includes('MISSING') ? 'warn' : 'ok',
      devStatus: output.includes('dev status') && output.includes('STALE') ? 'warn' : 'ok',
      coreArchive: output.includes('core archive') && output.includes('STALE') ? 'warn' : 'ok',
      memoryDecay: output.includes('archiving') ? 'warn' : 'ok',
      anchorIntegrity: output.includes('No anchor') ? 'warn' : 'ok',
      bidirectionalLinks: output.includes('incomplete') ? 'warn' : 'ok',
    };

    return {
      date: new Date().toISOString().split('T')[0],
      health,
      issues: [],
      suggestions: [],
      archivedCount: 0,
    };
  }
}

export { MemoryConfig, MaintenanceReport, DistillCheckResult, ProjectInfo } from './types.js';
