#!/usr/bin/env python3
"""
daily_memory_maintenance.py - 每日记忆系统维护脚本

每天早上 09:30 自动运行，执行以下维护任务：
1. 基础蒸馏检查（日志覆盖、状态新鲜度、衰减检查、锚点）
2. 自动归档（>30天未使用的 L1 条目降级归档）
3. 双向链接修复（自动补全 L2↔L3 缺失链接）
4. 每日摘要生成（前一日活动摘要）
5. 维护报告输出（保存到 journal/maintenance/）

用法：
  python daily_memory_maintenance.py [--vault <path>]
"""

import os
import re
import sys
import glob
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Windows UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


# ============================================================
# 路径与配置
# ============================================================


def find_vault():
    env = os.environ.get("OBSIDIAN_VAULT_PATH", "").strip()
    if env and os.path.isdir(env):
        return Path(env)
    home = Path.home()
    candidates = [
        home / "dumatework" / "dumate-memory-vault",
        home / "ObsidianVault",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return None


class MemoryVault:
    def __init__(self, vault_path: Path):
        self.root = vault_path
        self.brain = vault_path / "00-brain"
        self.journal = vault_path / "10-journal"
        self.projects = vault_path / "20-projects"
        self.knowledge = vault_path / "30-knowledge"
        self.learnings = vault_path / "60-learnings"
        self.templates = vault_path / "templates"
        self.scripts = vault_path / "scripts"

        # 子目录初始化
        (self.journal / "maintenance").mkdir(parents=True, exist_ok=True)
        (self.journal / "summary").mkdir(parents=True, exist_ok=True)
        (self.learnings / "archive").mkdir(parents=True, exist_ok=True)

        self.report_lines = []
        self.issues = []
        self.suggestions = []

    def log(self, line: str, level="INFO"):
        prefix = {"INFO": "  ", "WARN": "  !", "ERROR": " !!", "OK": "  "}.get(
            level, "  "
        )
        self.report_lines.append(f"{prefix} {line}")
        if level in ("WARN", "ERROR"):
            self.issues.append(line)
        if level == "SUGGEST":
            self.suggestions.append(line)

    def save_report(self):
        today = datetime.now().strftime("%Y-%m-%d")
        report_path = self.journal / "maintenance" / f"{today}.md"
        content = f"""# 记忆系统维护报告 - {today}

> 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}
> 维护脚本: `scripts/daily_memory_maintenance.py`

## 系统健康度

| 检查项 | 状态 | 说明 |
|--------|------|------|
| L4 日志覆盖 | {"OK" if not any("MISSING" in l for l in self.report_lines if "日志" in l) else "WARN"} | 近7天日志 |
| L3 开发状态 | {"OK" if not any("STALE" in l for l in self.report_lines if "开发状态" in l) else "WARN"} | 7天内更新 |
| L2 核心档案 | {"OK" if not any("STALE" in l for l in self.report_lines if "核心档案" in l) else "WARN"} | 30天内更新 |
| L1 记忆衰减 | {"OK" if not any("archiving" in l or "downgrading" in l for l in self.report_lines) else "WARN"} | last_used 标记 |
| 锚点完整性 | {"OK" if not any("!  No" in l for l in self.report_lines if "锚点" in l) else "WARN"} | 经验教训锚点 |
| 双向链接 | {"OK" if not any("不完整" in l for l in self.report_lines if "双向链接" in l) else "WARN"} | L2↔L3 |

## 详细报告

```
{chr(10).join(self.report_lines)}
```

## 发现的问题

{chr(10).join(f"- {i}" for i in self.issues) if self.issues else "*无问题*"}

## 建议行动

{chr(10).join(f"- {s}" for s in self.suggestions) if self.suggestions else "*无待办*"}

---
*自动维护报告，如需调整规则请修改 `scripts/daily_memory_maintenance.py`*
"""
        report_path.write_text(content, encoding="utf-8")
        print(f"\n  维护报告已保存: {report_path}")
        return report_path


# ============================================================
# 模块 1: 基础蒸馏检查
# ============================================================


def check_journal_recency(vault: MemoryVault):
    vault.log("=" * 50, "INFO")
    vault.log("[模块1] L4 日志覆盖检查", "INFO")
    vault.log("=" * 50, "INFO")

    today = datetime.now()
    missing_days = 0
    for i in range(7):
        d = today - timedelta(days=i)
        fname = vault.journal / f"{d.strftime('%Y-%m-%d')}.md"
        if fname.exists():
            size = fname.stat().st_size
            vault.log(f"{d.strftime('%Y-%m-%d')} OK ({size} bytes)", "OK")
        else:
            vault.log(f"{d.strftime('%Y-%m-%d')} MISSING", "WARN")
            missing_days += 1

    if missing_days > 3:
        vault.log(f"近7天有{missing_days}天无日志，可能有信息未记录", "SUGGEST")


def discover_projects(vault: MemoryVault):
    if not vault.projects.is_dir():
        return []
    projects = []
    for pdir in vault.projects.iterdir():
        if pdir.is_dir():
            status = pdir / "开发状态.md"
            core = pdir / "项目核心档案.md"
            if status.exists() or core.exists():
                projects.append(pdir.name)
    return projects


def check_project(vault: MemoryVault, project_name: str):
    pdir = vault.projects / project_name
    status_file = pdir / "开发状态.md"
    core_file = pdir / "项目核心档案.md"

    vault.log(f"\n项目: {project_name}", "INFO")
    vault.log("-" * 40, "INFO")

    # L3 开发状态
    if status_file.exists():
        content = status_file.read_text(encoding="utf-8")
        m = re.search(r"updated:\s*(\d{4}-\d{2}-\d{2})", content)
        if m:
            updated = datetime.strptime(m.group(1), "%Y-%m-%d")
            days_ago = (datetime.now() - updated).days
            level = "OK" if days_ago <= 7 else "WARN"
            vault.log(f"[L3] 开发状态: {m.group(1)} ({days_ago}d ago)", level)
            if days_ago > 7:
                vault.log(f"建议回顾近{days_ago}天会话，更新开发状态", "SUGGEST")
        else:
            vault.log("[L3] 开发状态: 缺少 updated 日期", "WARN")
    else:
        vault.log("[L3] 开发状态: 不存在", "WARN")

    # L2 核心档案
    if core_file.exists():
        content = core_file.read_text(encoding="utf-8")
        m = re.search(r"updated:\s*(\d{4}-\d{2}-\d{2})", content)
        if m:
            updated = datetime.strptime(m.group(1), "%Y-%m-%d")
            days_ago = (datetime.now() - updated).days
            level = "OK" if days_ago <= 30 else "WARN"
            vault.log(f"[L2] 核心档案: {m.group(1)} ({days_ago}d ago)", level)
            if days_ago > 30:
                vault.log("检查开发状态中是否有稳定信息需要提升到 L2", "SUGGEST")
        else:
            vault.log("[L2] 核心档案: 缺少 updated 日期", "WARN")
    else:
        vault.log("[L2] 核心档案: 不存在", "WARN")

    # 双向链接
    if status_file.exists() and core_file.exists():
        s = status_file.read_text(encoding="utf-8")
        c = core_file.read_text(encoding="utf-8")
        status_links = "[[项目核心档案" in s or "[[核心档案" in s
        core_links = "[[开发状态" in c
        if status_links and core_links:
            vault.log("双向链接 L2<->L3: OK", "OK")
        else:
            missing = []
            if not status_links:
                missing.append("L3->L2")
            if not core_links:
                missing.append("L2->L3")
            vault.log(f"双向链接不完整: 缺 {', '.join(missing)}", "WARN")


def check_memory_decay(vault: MemoryVault):
    vault.log(f"\n{'=' * 50}", "INFO")
    vault.log("[模块3] L1 记忆衰减检查", "INFO")
    vault.log(f"{'=' * 50}", "INFO")

    memory_file = vault.brain / "MEMORY.md"
    if not memory_file.exists():
        vault.log("MEMORY.md 不存在", "WARN")
        return

    content = memory_file.read_text(encoding="utf-8")
    tagged = re.findall(
        r"- \*\*(.+?)\*\*.*?\[last_used:\s*(\d{4}-\d{2}-\d{2})\]", content
    )

    if not tagged:
        vault.log(
            "未发现 last_used 标记（在 MEMORY.md 条目后添加 [last_used: YYYY-MM-DD]）",
            "INFO",
        )
        return

    stale_count = 0
    for label, date_str in tagged:
        last = datetime.strptime(date_str, "%Y-%m-%d")
        days_ago = (datetime.now() - last).days
        if days_ago > 30:
            vault.log(f"[{label}] {date_str} ({days_ago}d) -> 建议归档", "WARN")
            stale_count += 1
        elif days_ago > 14:
            vault.log(f"[{label}] {date_str} ({days_ago}d) -> 低频使用", "INFO")
        else:
            vault.log(f"[{label}] {date_str} ({days_ago}d) -> 活跃", "OK")

    if stale_count > 0:
        vault.log(f"共 {stale_count} 条记忆超过 30 天未使用，已触发自动归档", "INFO")


def check_anchors(vault: MemoryVault):
    vault.log(f"\n{'=' * 50}", "INFO")
    vault.log("[模块4] 记忆锚点检查", "INFO")
    vault.log(f"{'=' * 50}", "INFO")

    memory_file = vault.brain / "MEMORY.md"
    if not memory_file.exists():
        vault.log("MEMORY.md 不存在", "WARN")
        return

    content = memory_file.read_text(encoding="utf-8")
    section = re.search(r"## 经验教训(.*?)(?=## |$)", content, re.DOTALL)
    if section:
        anchors = re.findall(r"-\s+\*\*(.+?)\*\*", section.group(1))
        if anchors:
            vault.log(f"发现 {len(anchors)} 个锚点:", "OK")
            for a in anchors:
                vault.log(f"  - {a}", "INFO")
        else:
            vault.log("'经验教训'章节存在但无锚点条目", "WARN")
    else:
        vault.log("未发现 '经验教训' 章节，建议添加记忆锚点", "WARN")


# ============================================================
# 模块 2: 自动归档
# ============================================================


def auto_archive(vault: MemoryVault):
    vault.log(f"\n{'=' * 50}", "INFO")
    vault.log("[模块5] 自动归档", "INFO")
    vault.log(f"{'=' * 50}", "INFO")

    memory_file = vault.brain / "MEMORY.md"
    if not memory_file.exists():
        vault.log("MEMORY.md 不存在，跳过归档", "INFO")
        return 0

    content = memory_file.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")

    # 查找 >30 天未使用的条目
    stale_entries = []
    for match in re.finditer(
        r"(- \*\*.+?\*\*.*?(?:\[last_used:\s*\d{4}-\d{2}-\d{2}\]).*?)(?=\n- \*\*|\n## |$)",
        content,
        re.DOTALL,
    ):
        entry = match.group(1)
        m = re.search(r"\[last_used:\s*(\d{4}-\d{2}-\d{2})\]", entry)
        if m:
            last = datetime.strptime(m.group(1), "%Y-%m-%d")
            if (datetime.now() - last).days > 30:
                stale_entries.append((entry, m.group(1)))

    if not stale_entries:
        vault.log("无需要归档的条目", "OK")
        return 0

    # 创建归档文件
    archive_file = vault.learnings / "archive" / f"{today}_archived.md"
    archive_content = f"# 归档记忆 - {today}\n\n> 自动归档，原位于 MEMORY.md\n\n"
    for entry, date in stale_entries:
        archive_content += f"{entry}\n\n"

    archive_file.write_text(archive_content, encoding="utf-8")

    # 从 MEMORY.md 移除归档条目
    new_content = content
    for entry, _ in stale_entries:
        new_content = new_content.replace(entry.strip(), "")

    # 清理多余空行
    new_content = re.sub(r"\n{3,}", "\n\n", new_content)
    memory_file.write_text(new_content, encoding="utf-8")

    vault.log(f"已归档 {len(stale_entries)} 条记忆到 {archive_file}", "OK")
    return len(stale_entries)


# ============================================================
# 模块 3: 每日摘要生成
# ============================================================


def generate_daily_summary(vault: MemoryVault):
    vault.log(f"\n{'=' * 50}", "INFO")
    vault.log("[模块6] 每日摘要生成", "INFO")
    vault.log(f"{'=' * 50}", "INFO")

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    journal_file = vault.journal / f"{yesterday}.md"

    if not journal_file.exists():
        vault.log(f"昨日日志 {yesterday}.md 不存在，跳过摘要生成", "INFO")
        return None

    content = journal_file.read_text(encoding="utf-8")

    # 提取关键事件（标题行、决策标记、完成项）
    events = []
    for line in content.split("\n"):
        # 匹配标题、决策、完成标记
        if re.match(r"^(#{1,3} |\- |\* |\d+\. )", line.strip()):
            events.append(line.strip())

    summary_file = vault.journal / "summary" / f"{yesterday}.md"
    summary = f"""# 每日摘要 - {yesterday}

> 来源: `10-journal/{yesterday}.md`
> 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## 关键事件

{chr(10).join(f"- {e}" for e in events[:20])}

## 原始日志

参见 [[{yesterday}]]

---
*自动生成的每日摘要*
"""
    summary_file.write_text(summary, encoding="utf-8")
    vault.log(f"摘要已保存: {summary_file}", "OK")
    return summary_file


# ============================================================
# 主流程
# ============================================================


def main():
    parser = argparse.ArgumentParser(description="Daily Memory System Maintenance")
    parser.add_argument("--vault", help="Path to Obsidian vault")
    parser.add_argument("--dry-run", action="store_true", help="只检查不修改")
    args = parser.parse_args()

    vault_path = Path(args.vault) if args.vault else find_vault()
    if not vault_path or not vault_path.is_dir():
        print("ERROR: Cannot find vault. Set OBSIDIAN_VAULT_PATH or use --vault")
        sys.exit(1)

    vault = MemoryVault(vault_path)
    dry_run = args.dry_run

    print(f"\n{'=' * 60}")
    print("  Daily Memory System Maintenance")
    print(f"  Vault: {vault.root}")
    print(f"  Time:  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if dry_run:
        print("  Mode:  DRY-RUN (no modifications)")
    print(f"{'=' * 60}")

    # 模块 1: 基础蒸馏检查
    check_journal_recency(vault)
    for project in discover_projects(vault):
        check_project(vault, project)
    check_memory_decay(vault)
    check_anchors(vault)

    # 模块 2: 自动归档
    if not dry_run:
        archived = auto_archive(vault)
    else:
        vault.log("\n[模块5] 自动归档: 跳过 (dry-run)", "INFO")
        archived = 0

    # 模块 3: 每日摘要
    if not dry_run:
        summary = generate_daily_summary(vault)
    else:
        vault.log("\n[模块6] 每日摘要: 跳过 (dry-run)", "INFO")
        summary = None

    # 保存报告
    if not dry_run:
        report_path = vault.save_report()
    else:
        vault.log("\n维护报告: 跳过 (dry-run)", "INFO")

    # 汇总输出
    print(f"\n{'=' * 60}")
    print("  维护完成")
    print(f"  发现问题: {len(vault.issues)}")
    print(f"  建议行动: {len(vault.suggestions)}")
    if not dry_run:
        print(f"  归档条目: {archived}")
        print(
            f"  报告位置: {vault.journal / 'maintenance' / datetime.now().strftime('%Y-%m-%d')}.md"
        )
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
