# TraceMind

[English](README_en.md) | [中文版](README.md)

**TraceMind** is first and foremost a Project-Local Memory engine deployed and mounted as an AI **Skill**. Powered entirely by bundled Python scripts, it provides AI agents (like Cursor, Windsurf, Claude Code, Antigravity, OpenCode) with persistent, project-specific memory—including a timeline of events, known facts, hooks, and strategy records—without requiring a complex MCP (Model Context Protocol) configuration.

## Features

- **Zero-config SQLite Storage**: Automatically initializes `.mpm-data/mcp_memory.db` in your project root.
- **Timeline & Memos**: Record a memo after any code or document changes (`memo.py`) and render them into a beautiful HTML timeline (`timeline.py`).
- **Smart Recall**: Uses a "Broad-in, Strict-out" fuzzy expansion algorithm (`recall.py`) to flawlessly retrieve history even if the agent slightly misremembers the exact keywords.
- **3-Step Reflection Flow**: After solving complex or stubborn tasks, the AI automatically executes a unified loop: "Record the raw history -> Cross-reference past pitfalls -> Extract new rules". This maximizes learning while minimizing context window waste.
- **Fast Experience Evolution**: Solidify reusable lessons, pitfalls, and "known facts" (`remember.py`). With an optimized confidence algorithm, once a candidate lesson is validated, it immediately breaches the threshold and is autonomously injected back into the IDE's system rules (e.g., `AGENTS.md` or `.cursor/rules/tracemind.mdc`).
- **Task Hooks**: Suspend, list, or release pending hooks (`hook.py`) when work is blocked.

## Architecture

1. **LLM Cognitive Layer**: The AI agent reads the standard `references/rules-create.md` to intelligently write/append the `TraceMind Protocol` into your target IDE's rules file, ensuring existing complex Markdown structures or YAML frontmatters aren't broken.
2. **Script Execution Layer**: Standard Python scripts handle database CRUD, HTML generation, and log snapshots.

## Usage

Please refer to [`SKILL.md`](./SKILL.md) and [`references/tracemind-protocol.md`](./references/tracemind-protocol.md) for the exact Agent rules, trigger language, and protocol instructions.
