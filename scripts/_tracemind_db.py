from __future__ import annotations

import argparse
import difflib
import html
import json
import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DATA_DIR = ".mpm-data"
DB_NAME = "mcp_memory.db"
TRACE_MIND_FACTS_BEGIN = "<!-- TraceMind Facts Begin -->"
TRACE_MIND_FACTS_END = "<!-- TraceMind Facts End -->"
TRACE_MIND_RULES_BLOCK = """## TraceMind Protocol

Use TraceMind for project-local memory. The TraceMind skill provides Python scripts; no MCP configuration is required.
Do not use MPM tools for TraceMind runtime; use the bundled scripts directly.

Use the current project root as `--root .` unless the user explicitly names another root.

Required behavior:

- After important code, document, architecture, debugging, validation, or decision changes, record a memo:
  `python <tracemind-skill-dir>/scripts/memo.py add "why this changed" --root . --category 修改 --entity "Entity" --act "Action" --path "relative/path"`
- To recall project history, brainstorm multiple synonyms to overcome strict SQL matching (e.g., "按钮 按键 button"), then use:
  `python <tracemind-skill-dir>/scripts/recall.py "synonym1 synonym2 synonym3" --root . [--category "OptionalTag"]`
- To render the timeline, use:
  `python <tracemind-skill-dir>/scripts/timeline.py --root .`
- When the user says "记住", "记住了", "记下来", "铁律", "避坑", "经验", "known fact", or "策略记忆", use:
  `python <tracemind-skill-dir>/scripts/remember.py ... --root .`
- When work is blocked, pending, waiting for confirmation, or should become a todo/hook, use:
  `python <tracemind-skill-dir>/scripts/hook.py ... --root .`

Keep memo history, known facts, and hooks separate.

Stable known facts can be promoted into a `TraceMind Facts` block when after-action shows repeated adoption and high confidence.
"""


def project_root(value: str | None = None) -> Path:
    root = Path(value or ".").resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"project root is not a directory: {root}")
    return root


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def find_project_rules_files(root: Path) -> list[Path]:
    candidates = [
        root / "AGENTS.md",
        root / "GEMINI.md",
        root / "CLAUDE.md",
        root / ".hermes.md",
        root / "HERMES.md",
        root / "IDENTITY.md",
        root / "SOUL.md",
        root / ".openclaw.md",
        root / ".agents/rules/tracemind.md",
        root / ".agent/rules/tracemind.md",
        root / ".claude/CLAUDE.md",
        root / ".claude/rules/tracemind.md",
        root / "AGENTS.override.md",
        root / ".cursor/rules/tracemind.mdc",
        root / ".windsurf/rules/tracemind.md",
        root / ".kiro/steering/tracemind.md",
    ]
    res = []
    for p in candidates:
        if p.exists():
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                if "TraceMind Protocol" in content:
                    res.append(p)
            except Exception:
                pass
    return res


def bootstrap_project(root: Path) -> None:
    db_path(root).parent.mkdir(parents=True, exist_ok=True)
    dev_log_archive_path(root).parent.mkdir(parents=True, exist_ok=True)



def db_path(root: Path) -> Path:
    return root / DATA_DIR / DB_NAME


def dev_log_path(root: Path) -> Path:
    return root / "dev-log.md"


def dev_log_archive_path(root: Path) -> Path:
    return root / "dev-log-archive" / "memo_archive.jsonl"


def connect(root: Path) -> sqlite3.Connection:
    path = db_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    ensure_schema(conn)
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS memos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL DEFAULT '开发',
            entity TEXT NOT NULL DEFAULT 'System',
            act TEXT NOT NULL DEFAULT 'Manual Entry',
            path TEXT NOT NULL DEFAULT '-',
            content TEXT NOT NULL,
            session_id TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS known_facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL DEFAULT 'rule',
            summarize TEXT NOT NULL,
            scope TEXT NOT NULL DEFAULT 'project',
            keywords TEXT,
            confidence REAL DEFAULT 0.45,
            support_count INTEGER DEFAULT 0,
            hit_count INTEGER DEFAULT 0,
            adopt_count INTEGER DEFAULT 0,
            reject_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'candidate',
            source_type TEXT DEFAULT 'manual',
            source_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS fact_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            fact_id INTEGER,
            task_id TEXT,
            phase TEXT,
            context_signature TEXT,
            payload_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fact_id) REFERENCES known_facts(id)
        );

        CREATE TABLE IF NOT EXISTS pending_hooks (
            hook_id TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            context TEXT,
            tag TEXT,
            status TEXT DEFAULT 'open',
            related_task_id TEXT,
            result_summary TEXT,
            expires_at TEXT,
            summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_memos_category ON memos(category);
        CREATE INDEX IF NOT EXISTS idx_memos_entity ON memos(entity);
        CREATE INDEX IF NOT EXISTS idx_memos_timestamp ON memos(timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_known_facts_status ON known_facts(status);
        CREATE INDEX IF NOT EXISTS idx_pending_hooks_status ON pending_hooks(status, created_at);
        """
    )
    conn.commit()


def project_name(root: Path) -> str:
    return root.name or root.resolve().name


def csv_words(value: str) -> list[str]:
    return [part.strip() for part in value.replace(",", " ").split() if part.strip()]


def like_filter(columns: Iterable[str], words: list[str], params: list[str]) -> str:
    if not words:
        return ""
    groups = []
    for word in words:
        groups.append("(" + " OR ".join(f"{col} LIKE ?" for col in columns) + ")")
        params.extend([f"%{word}%"] * len(list(columns)))
    return " AND (" + " OR ".join(groups) + ")"


def like_score(columns: Iterable[str], words: list[str], params: list[str]) -> str:
    if not words:
        return "0"
    groups = []
    for word in words:
        groups.append("(" + " OR ".join(f"{col} LIKE ?" for col in columns) + ")")
        params.extend([f"%{word}%"] * len(list(columns)))
    return " + ".join(groups)


def exact_score(columns: Iterable[str], phrase: str, params: list[str]) -> str:
    phrase = phrase.strip()
    if not phrase:
        return "0"
    conditions = []
    for col in columns:
        conditions.append(f"{col} LIKE ?")
        params.append(f"%{phrase}%")
    return "(" + " OR ".join(conditions) + ")"


def expand_fuzzy_keywords(conn: sqlite3.Connection, words: list[str], cutoff: float = 0.5) -> list[str]:
    cursor = conn.execute(
        "SELECT DISTINCT entity FROM memos UNION SELECT DISTINCT category FROM memos"
    )
    index_pool = [row[0] for row in cursor.fetchall() if row[0]]
    
    expanded = set(words)
    for w in words:
        matches = difflib.get_close_matches(w, index_pool, n=3, cutoff=cutoff)
        expanded.update(matches)
    return list(expanded)


def session_id() -> str:
    return f"{time.time_ns():x}"[:8]


def now_text() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Context:
    task: str = ""
    task_id: str = ""
    intent: str = ""
    phase: str = ""
    risk: str = ""
    files: str = ""
    symbols: str = ""
    tools: str = ""

    def keywords(self) -> str:
        return " ".join(
            part
            for part in [
                self.task,
                self.intent,
                self.phase,
                self.risk,
                self.files,
                self.symbols,
                self.tools,
            ]
            if part
        )

    def scope(self) -> str:
        if self.files:
            return f"path:{self.files.split(',')[0].strip()}"
        if self.symbols:
            return f"symbol:{self.symbols.split(',')[0].strip()}"
        if self.task_id:
            return f"task:{self.task_id}"
        return "project"


def add_context_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--task", default="")
    parser.add_argument("--task-id", default="")
    parser.add_argument("--intent", default="")
    parser.add_argument("--phase", default="")
    parser.add_argument("--risk", default="")
    parser.add_argument("--files", default="")
    parser.add_argument("--symbols", default="")
    parser.add_argument("--tools", default="")


def context_from_args(args: argparse.Namespace) -> Context:
    return Context(
        task=args.task,
        task_id=args.task_id,
        intent=args.intent,
        phase=args.phase,
        risk=args.risk,
        files=args.files,
        symbols=args.symbols,
        tools=args.tools,
    )


def print_rows(title: str, rows: Iterable[sqlite3.Row], formatter) -> None:
    rows = list(rows)
    print(f"{title} ({len(rows)}):")
    if not rows:
        print("- none")
        return
    for row in rows:
        print(formatter(row))


def escape(value: object) -> str:
    return html.escape("" if value is None else str(value))


def json_payload(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def memo_archive_entry(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "category": row["category"],
        "entity": row["entity"],
        "act": row["act"],
        "path": row["path"],
        "content": row["content"],
        "session_id": row["session_id"],
        "timestamp": row["timestamp"],
    }


def _render_trace_mind_facts_block(rows: Iterable[sqlite3.Row]) -> str:
    lines = [TRACE_MIND_FACTS_BEGIN, "## TraceMind Facts", ""]
    rows = list(rows)
    if not rows:
        lines.append("- none")
    else:
        for row in rows:
            lines.append(
                f"- [fact_id={row['id']} conf={row['confidence']:.2f} adopts={row['adopt_count']}] {row['summarize']}"
            )
    lines.append(TRACE_MIND_FACTS_END)
    return "\n".join(lines) + "\n"


def sync_trace_mind_facts(root: Path, conn: sqlite3.Connection, min_adopt_count: int = 1, min_confidence: float = 0.60) -> Path:
    rows = conn.execute(
        """
        SELECT * FROM known_facts
        WHERE status NOT IN ('rejected', 'archived', 'superseded')
          AND adopt_count >= ?
          AND confidence >= ?
        ORDER BY confidence DESC, updated_at DESC, id DESC
        """,
        (min_adopt_count, min_confidence),
    ).fetchall()

    block = _render_trace_mind_facts_block(rows)
    pattern = re.compile(r"\n?<!-- TraceMind Facts Begin -->.*?<!-- TraceMind Facts End -->\n?", re.S)

    paths = find_project_rules_files(root)
    if not paths:
        paths = [root / "AGENTS.md"]
        
    last_path = root / "AGENTS.md"
    for path in paths:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            existing = ""
        else:
            existing = path.read_text(encoding="utf-8", errors="ignore")
            
        if rows:
            if pattern.search(existing):
                updated = pattern.sub("\n" + block, existing).rstrip() + "\n"
            else:
                updated = existing
                if updated and not updated.endswith("\n"):
                    updated += "\n"
                if updated and not updated.endswith("\n\n"):
                    updated += "\n"
                updated += block
        else:
            if not pattern.search(existing):
                last_path = path
                continue
            updated = pattern.sub("\n", existing).rstrip() + "\n"

        path.write_text(updated, encoding="utf-8")
        last_path = path
    return last_path



def sync_dev_log(root: Path, conn: sqlite3.Connection, limit: int = 100) -> Path:
    rows = conn.execute("SELECT * FROM memos ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    lines = [
        f"# Dev Log: {project_name(root)} (Surgical Snapshot)",
        "",
        "<!-- 由 TraceMind skill 自动生成，请勿手动编辑 -->",
        "",
    ]
    for row in rows:
        lines.append(
            f"- [{row['content']}] **{row['timestamp']}**: {row['category']} ({row['entity']}) {row['act']}"
        )
    path = dev_log_path(root)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def append_dev_log_archive(root: Path, row: sqlite3.Row) -> Path:
    path = dev_log_archive_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(memo_archive_entry(row), ensure_ascii=False) + "\n")
    return path
