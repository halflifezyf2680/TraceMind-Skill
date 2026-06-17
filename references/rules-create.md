# Creating Project-Level TraceMind Rules

Create a project-level rules file for the current agent/IDE/CLI. Use only repository/workspace-scoped locations. If the environment already has a project rules file, append the TraceMind block instead of replacing existing rules.

## Verified Project Rule Files

| Host | Project/workspace rule file |
| --- | --- |
| Codex | `AGENTS.md` at the project root; nested `AGENTS.md` for narrower directories. Use `AGENTS.override.md` only when an explicit override is needed. |
| Claude Code | `CLAUDE.md` or `.claude/CLAUDE.md`; for modular rules use `.claude/rules/tracemind.md`. |
| Gemini CLI / Antigravity | `.agents/rules/tracemind.md` (inside workspace or git root) or legacy `.agent/rules/`. |
| Cursor | `.cursor/rules/tracemind.mdc`; root `AGENTS.md` is a simple alternative. Legacy `.cursorrules` is still recognized but deprecated. |
| Windsurf / Cascade | `.windsurf/rules/tracemind.md`; workspace `AGENTS.md` files are also processed by the rules engine. |
| Kiro | `.kiro/steering/tracemind.md`; root `AGENTS.md` is also supported. |
| OpenClaw | `AGENTS.md` at the project root (part of the bootstrap file family, along with `SOUL.md` etc.). `.openclaw.md` is also detected. |
| OpenCode | `AGENTS.md` at the project root. Can be auto-generated via `/init`, with task-specific files in `.opencode/agents/`. |
| Hermes | `AGENTS.md` at the project root. `.hermes.md` or `HERMES.md` are also supported and often used for highest-priority per-repo configs. |
| Unknown host | `AGENTS.md` at the project root. |

Avoid writing user/global files such as `~/.claude/CLAUDE.md`, `~/.gemini/GEMINI.md`, `~/.codeium/windsurf/memories/global_rules.md`, or `~/.kiro/steering/` when the task is project-level setup.

## TraceMind Rules Block

Paste this block into the project rules file:

```markdown
## TraceMind Protocol

Use TraceMind for project-local memory. The TraceMind skill provides Python scripts; no MCP configuration is required.

Initialize once per project/session when needed:

`python <tracemind-skill-dir>/scripts/init.py --root .`

Use the current project root as `--root .` unless the user explicitly names another root.

Required behavior for specific triggers:
- To render the timeline, use:
  `python <tracemind-skill-dir>/scripts/timeline.py --root .`
- When the user explicitly says "记住", "铁律", "避坑", "known fact", use `remember.py add`.
- When work is blocked, pending, waiting for confirmation, use `hook.py`.

Lifecycle Hooks (MANDATORY for every task):

**1. BEFORE starting work (Context Loading):**
- Check for known pitfalls before coding:
  `python <tracemind-skill-dir>/scripts/remember.py before-action --root . --task "brief task description"`

**2. AFTER completing a complex, stubborn, or major phased task (The 3-Step Reflection Flow):**
To save tokens, do NOT run this for trivial edits. But for major milestones or hard-to-fix bugs, you MUST execute this 3-step sequence:
- Step 1 (Record): Log the raw history into the timeline.
  `python <tracemind-skill-dir>/scripts/memo.py add "why this changed" --root . --category 修改 --entity "Entity" --act "Action" --path "relative/path"`
- Step 2 (Cross-Check): Check if you've tripped over this component/issue in the past.
  `python <tracemind-skill-dir>/scripts/recall.py "keywords of changed component"`
- Step 3 (Abstract & Evolve): Autonomously reflect on the recall results and your current work. Use `--observe` to extract new pitfalls or patterns as candidates.
  `python <tracemind-skill-dir>/scripts/remember.py after-action --root . --result success --adopted "<id>" --observe "Extracted lesson 1||Extracted lesson 2"`

Keep memo history, known facts, and hooks separate.
```

Replace `<tracemind-skill-dir>` with the actual skill directory path if the host rules file does not support variables.

## Validation

After creating rules:

1. Confirm the file exists.
2. Confirm it includes "TraceMind Protocol".
3. Run `python <tracemind-skill-dir>/scripts/init.py --root .`.
4. Verify `.mpm-data/mcp_memory.db` exists.

## Source Notes

Verified against official documentation on 2026-06-04:

- Codex project instructions: `AGENTS.md` / `AGENTS.override.md`
- Claude Code memory: `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/*.md`
- Gemini CLI / Antigravity context: workspace `.agents/rules/`; user-global `~/.gemini/GEMINI.md`
- Cursor rules: `.cursor/rules`
- Windsurf/Cascade rules: `.windsurf/rules/*.md`, workspace `AGENTS.md`
- Kiro steering: `.kiro/steering/`, root `AGENTS.md`
