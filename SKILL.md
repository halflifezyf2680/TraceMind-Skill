---
name: tracemind
description: "Project memory skill using bundled Python scripts, no MCP required. Use when Codex needs project-local memory: initialize TraceMind storage, record important changes, recall project history, remember reusable lessons (记住, 记下来, 铁律, 避坑, known facts), manage pending hooks/todos, render a project timeline, or create project-level rules for TraceMind usage."
---

# TraceMind

TraceMind is project-local memory powered by bundled Python scripts. It does not require MCP configuration.
Do not use MPM tools for TraceMind runtime; use the bundled scripts directly.

Always treat the current workspace root as the project root unless the user explicitly names another root.
On first use in a project, TraceMind should bootstrap the environment:
1. The LLM identifies the active agent/IDE host (e.g. Antigravity, Claude Code, Cursor).
2. The LLM writes the TraceMind Protocol rules block directly to the host-specific rule file path (refer to [rules-create.md](file:///d:/AI_Project/harness-skill/tracemind/references/rules-create.md)).
3. The LLM runs the initialization script to initialize storage:
   `python <tracemind-skill-dir>/scripts/init.py --root .`

## Action Map

Run scripts from this skill's bundled `scripts/` directory.

| Need | Script |
| --- | --- |
| First use in a project | `python <tracemind-skill-dir>/scripts/init.py --root <project-root>` |
| Record important project history | `python <tracemind-skill-dir>/scripts/memo.py add "..." --root <project-root>` |
| Search memo history | `python <tracemind-skill-dir>/scripts/recall.py "keywords" --root <project-root>` |
| Render timeline HTML | `python <tracemind-skill-dir>/scripts/timeline.py --root <project-root>` |
| Remember a reusable rule, lesson, pitfall, or "记住" fact | `python <tracemind-skill-dir>/scripts/remember.py add "..." --root <project-root>` |
| Recall known facts before work | `python <tracemind-skill-dir>/scripts/remember.py before-action --root <project-root> --task "..."` |
| Update known facts after work | `python <tracemind-skill-dir>/scripts/remember.py after-action --root <project-root> --result success --adopted 1 --observe "..."` |
| Create/list/release pending hooks | `python <tracemind-skill-dir>/scripts/hook.py create/list/release ... --root <project-root>` |

Do not expect Codex to remember many modes. Choose the script by action name first, then use `--help` if arguments are unclear.

## Protocol

1. At the start of TraceMind work, initialize rules and storage:
   * First, you MUST use the `view_file` tool to read `references/rules-create.md`. This file contains the exact TraceMind Protocol rules block and the mapping of host agents to their specific rules file paths.
   * Then, identify the active host agent and use your code editing tools to manually write/append that exact rules block directly to the host-specific rules path. Do NOT hallucinate or guess the rules block. Do not rely on scripts to create this file, as hardcoded scripts may not respect existing file structures or formats.
   * Then run the initialization script to initialize storage:
     ```powershell
     python <tracemind-skill-dir>/scripts/init.py --root .
     ```
     This initializes `.mpm-data/mcp_memory.db` and the `dev-log.md` snapshot.
2. **Before starting work (Context Loading)**:
   Run `python <tracemind-skill-dir>/scripts/remember.py before-action --root . --task "..."` to check for known pitfalls.
3. **After completing a complex, stubborn, or major phased task (The 3-Step Reflection Flow)**:
   To save tokens, do NOT run this for trivial edits. But for major milestones or hard-to-fix bugs, execute this sequence:
   * **Step 1 (Record)**: Log the raw change history:
     `python <tracemind-skill-dir>/scripts/memo.py add "why this changed" --root . --category 修改 --entity "Entity" --act "Action" --path "path"`
   * **Step 2 (Cross-Check)**: Check if you've tripped over this issue in the past:
     `python <tracemind-skill-dir>/scripts/recall.py "keywords"`
   * **Step 3 (Abstract & Evolve)**: Autonomously extract new patterns using `--observe`:
     `python <tracemind-skill-dir>/scripts/remember.py after-action --root . --result success --adopted "<id>" --observe "Extracted lesson 1"`
4. When the user explicitly says "记住", "铁律", "避坑", or "known fact", use `remember.py add`.
5. When work is blocked, pending, or waiting for confirmation, use `hook.py`.

For the exact protocol and trigger language, read `references/tracemind-protocol.md`.

## Project Rules

When asked to install or document TraceMind rules for an agent/IDE/CLI, read `references/rules-create.md`.

Use that reference to create a project-level rules file such as `AGENTS.md`, `CLAUDE.md`, or an IDE-specific rules file. You MUST copy the exact text from the template in the reference. Do NOT hallucinate, invent, or guess the TraceMind Protocol rules.

## Storage

TraceMind creates SQLite storage under the project root:

```text
.mpm-data/mcp_memory.db
```

The scripts use only Python standard library modules.
