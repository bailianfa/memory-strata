#!/usr/bin/env node
import { Command } from 'commander';
import { MemoryStrata } from './index.js';

const program = new Command();

program
  .name('pi-memory-strata')
  .description('Four-layer stratified memory architecture for long-horizon AI agent projects')
  .version('0.1.0');

program
  .command('check')
  .description('Run distillation check on memory system')
  .option('-v, --vault <path>', 'Path to Obsidian vault')
  .action(async (options) => {
    const strata = new MemoryStrata({ vaultPath: options.vault });
    try {
      const result = await strata.check();
      console.log('Distillation check completed:', result.ok ? 'OK' : 'WARN');
      if (!result.ok) {
        process.exit(1);
      }
    } catch (err) {
      console.error('Check failed:', err instanceof Error ? err.message : String(err));
      process.exit(1);
    }
  });

program
  .command('maintain')
  .description('Run daily maintenance routine')
  .option('-v, --vault <path>', 'Path to Obsidian vault')
  .option('--dry-run', 'Only check, do not modify')
  .action(async (options) => {
    const strata = new MemoryStrata({ vaultPath: options.vault });
    try {
      const report = await strata.maintain();
      console.log('Maintenance completed:', report.date);
      console.log('Health:', JSON.stringify(report.health, null, 2));
      console.log('Issues:', report.issues.length);
      console.log('Suggestions:', report.suggestions.length);
    } catch (err) {
      console.error('Maintenance failed:', err instanceof Error ? err.message : String(err));
      process.exit(1);
    }
  });

program
  .command('init-project')
  .description('Initialize a new project in the vault')
  .argument('<name>', 'Project name')
  .option('-v, --vault <path>', 'Path to Obsidian vault')
  .action((name, options) => {
    const strata = new MemoryStrata({ vaultPath: options.vault });
    try {
      strata.initProject(name);
      console.log(`Project initialized: ${name}`);
    } catch (err) {
      console.error('Init failed:', err instanceof Error ? err.message : String(err));
      process.exit(1);
    }
  });

program.parse();
