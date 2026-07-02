#!/usr/bin/env python3
"""
memory_distill_check.py - Memory Strata 蒸馏检查工具

检查四层记忆系统的状态，提示需要蒸馏的内容。
适用于任何使用 memory-strata 架构的项目。

用法：
  python memory_distill_check.py                           # 自动扫描所有项目
  python memory_distill_check.py --project MyProject       # 检查指定项目

功能：
1. 扫描每日日志，检查近7天覆盖情况
2. 检查各项目开发状态的新鲜度
3. 检查各项目核心档案的新鲜度
4. 检查 MEMORY.md 的 last_used 标记，提示衰减
5. 检查记忆锚点完整性
"""

import os
import re
import glob
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Windows UTF-8 输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def find_vault():
    """自动发现 Obsidian vault 路径"""
    # 1. 环境变量
    env = os.environ.get("OBSIDIAN_VAULT_PATH", "").strip()
    if env and os.path.isdir(env):
        return env
    # 2. 常见位置
    home = Path.home()
    candidates = [
        home / "dumatework" / "dumate-memory-vault",
        home / "ObsidianVault",
        home / "vault",
    ]
    for c in candidates:
        if c.is_dir():
            return str(c)
    return None


def discover_projects(vault):
    """自动发现 vault 中的项目"""
    projects_dir = os.path.join(vault, "20-projects")
    if not os.path.isdir(projects_dir):
        return []
    projects = []
    for name in os.listdir(projects_dir):
        pdir = os.path.join(projects_dir, name)
        if os.path.isdir(pdir):
            status = os.path.join(pdir, "开发状态.md")
            core = os.path.join(pdir, "项目核心档案.md")
            if os.path.exists(status) or os.path.exists(core):
                projects.append(name)
    return projects


def check_journal_recency(vault):
    """检查最近日志的覆盖情况"""
    print("\n" + "=" * 60)
    print("[1] 日志覆盖检查 (L4)")
    print("=" * 60)

    journal_dir = os.path.join(vault, "10-journal")
    if not os.path.isdir(journal_dir):
        print("  ! 10-journal 目录不存在，跳过")
        return

    today = datetime.now()
    lines = []
    for i in range(7):
        d = today - timedelta(days=i)
        fname = os.path.join(journal_dir, f"{d.strftime('%Y-%m-%d')}.md")
        if os.path.exists(fname):
            size = os.path.getsize(fname)
            lines.append(f"  {d.strftime('%Y-%m-%d')} OK ({size} bytes)")
        else:
            lines.append(f"  {d.strftime('%Y-%m-%d')} MISSING")

    for line in lines:
        print(line)

    missing = sum(1 for l in lines if "MISSING" in l)
    if missing > 3:
        print(f"\n  ! 近7天有{missing}天无日志，可能有信息未记录")


def check_project(vault, project_name):
    """检查单个项目的记忆状态"""
    pdir = os.path.join(vault, "20-projects", project_name)
    status_file = os.path.join(pdir, "开发状态.md")
    core_file = os.path.join(pdir, "项目核心档案.md")

    print(f"\n{'=' * 60}")
    print(f"  项目: {project_name}")
    print(f"{'=' * 60}")

    # 开发状态新鲜度 (L3)
    if os.path.exists(status_file):
        with open(status_file, "r", encoding="utf-8") as f:
            content = f.read()
        m = re.search(r"updated:\s*(\d{4}-\d{2}-\d{2})", content)
        if m:
            updated = datetime.strptime(m.group(1), "%Y-%m-%d")
            days_ago = (datetime.now() - updated).days
            icon = "OK" if days_ago <= 7 else "STALE"
            print(f"  [L3] 开发状态: updated {m.group(1)} ({days_ago}d ago) {icon}")
            if days_ago > 7:
                print(f"       -> 建议回顾近{days_ago}天的会话，更新开发状态")
        else:
            print(f"  [L3] 开发状态: 缺少 updated 日期")
    else:
        print(f"  [L3] 开发状态: 不存在")

    # 核心档案新鲜度 (L2)
    if os.path.exists(core_file):
        with open(core_file, "r", encoding="utf-8") as f:
            content = f.read()
        m = re.search(r"updated:\s*(\d{4}-\d{2}-\d{2})", content)
        if m:
            updated = datetime.strptime(m.group(1), "%Y-%m-%d")
            days_ago = (datetime.now() - updated).days
            icon = "OK" if days_ago <= 30 else "STALE"
            print(f"  [L2] 核心档案: updated {m.group(1)} ({days_ago}d ago) {icon}")
            if days_ago > 30:
                print(f"       -> 检查开发状态中是否有稳定信息需要提升")
        else:
            print(f"  [L2] 核心档案: 缺少 updated 日期")
    else:
        print(f"  [L2] 核心档案: 不存在")

    # 检查双向链接
    if os.path.exists(status_file) and os.path.exists(core_file):
        with open(status_file, "r", encoding="utf-8") as f:
            s = f.read()
        with open(core_file, "r", encoding="utf-8") as f:
            c = f.read()
        status_links_core = "[[项目核心档案" in s or "[[核心档案" in s
        core_links_status = "[[开发状态" in c
        if status_links_core and core_links_status:
            print(f"  [LINK] L2 <-> L3 双向链接: OK")
        else:
            missing_links = []
            if not status_links_core:
                missing_links.append("L3->L2")
            if not core_links_status:
                missing_links.append("L2->L3")
            print(f"  [LINK] 双向链接不完整: 缺 {', '.join(missing_links)}")


def check_memory_last_used(vault):
    """检查 MEMORY.md 中记忆的 last_used 标记 (L1)"""
    print("\n" + "=" * 60)
    print("[L1] 记忆强度衰减检查 (last_used)")
    print("=" * 60)

    memory_file = os.path.join(vault, "00-brain", "MEMORY.md")
    if not os.path.exists(memory_file):
        print("  ! MEMORY.md 不存在")
        return

    with open(memory_file, "r", encoding="utf-8") as f:
        content = f.read()

    tagged = re.findall(
        r"- \*\*(.+?)\*\*.*?\[last_used:\s*(\d{4}-\d{2}-\d{2})\]", content
    )

    if not tagged:
        print(
            "  (no last_used tags found - add [last_used: YYYY-MM-DD] to your MEMORY.md entries)"
        )
        return

    today = datetime.now()
    stale = 0
    for label, date_str in tagged:
        last = datetime.strptime(date_str, "%Y-%m-%d")
        days_ago = (today - last).days
        if days_ago > 30:
            print(
                f"  !! [{label}] last_used: {date_str} ({days_ago}d ago) -> consider archiving"
            )
            stale += 1
        elif days_ago > 14:
            print(
                f"  !  [{label}] last_used: {date_str} ({days_ago}d ago) -> rarely used"
            )
        else:
            print(f"  OK [{label}] last_used: {date_str} ({days_ago}d ago)")

    if stale > 0:
        print(f"\n  {stale} entries >30d unused, consider downgrading to L3/L4")


def check_anchors(vault):
    """检查记忆锚点是否完整 (L1)"""
    print("\n" + "=" * 60)
    print("[L1] 记忆锚点检查")
    print("=" * 60)

    memory_file = os.path.join(vault, "00-brain", "MEMORY.md")
    if not os.path.exists(memory_file):
        print("  ! MEMORY.md 不存在")
        return

    with open(memory_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 查找"经验教训"或"锚点"部分中的条目
    anchor_section = re.search(r"## 经验教训(.*?)(?=##|$)", content, re.DOTALL)
    if anchor_section:
        anchors = re.findall(r"-\s+\*\*(.+?)\*\*", anchor_section.group(1))
        if anchors:
            print(f"  Found {len(anchors)} anchor(s) in MEMORY.md:")
            for a in anchors:
                print(f"    - {a}")
        else:
            print("  ! '经验教训' section exists but has no anchors")
    else:
        print("  ! No '经验教训' section found in MEMORY.md")
        print("    -> Add a '## 经验教训' section with memory anchors")


def main():
    parser = argparse.ArgumentParser(description="Memory Strata - Distillation Check")
    parser.add_argument("--project", help="Check a specific project")
    parser.add_argument("--vault", help="Path to Obsidian vault")
    args = parser.parse_args()

    vault = args.vault or find_vault()
    if not vault:
        print(
            "ERROR: Cannot find Obsidian vault. Set OBSIDIAN_VAULT_PATH or use --vault"
        )
        sys.exit(1)

    print(f"\nMemory Strata - Distillation Check")
    print(f"  Vault: {vault}")
    print(f"  Date:  {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # L4 日志覆盖
    check_journal_recency(vault)

    # 项目状态
    if args.project:
        projects = [args.project]
    else:
        projects = discover_projects(vault)

    if projects:
        for p in projects:
            check_project(vault, p)
    else:
        print("\n  (No projects found in 20-projects/)")

    # L1 衰减检查
    check_memory_last_used(vault)

    # L1 锚点检查
    check_anchors(vault)

    print("\n" + "=" * 60)
    print(
        "Check complete. Follow the suggestions above to maintain your memory system."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
