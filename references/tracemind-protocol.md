# TraceMind Protocol

Use this protocol with the bundled scripts in `../scripts/`.

## Tool Equivalents

- `init.py`: initialize `.mpm-data/mcp_memory.db` in the project root.
- `init.py`: initialize `.mpm-data/mcp_memory.db` and bootstrap `dev-log.md`.
- `memo.py`: record or search project timeline events.
- `memo.py`: record or search project timeline events, and keep `dev-log.md` plus `dev-log-archive/memo_archive.jsonl` in sync.
- `recall.py`: search memo history only. It does not return known facts.
- `timeline.py`: render `project_timeline.html` from memo events.
- `remember.py`: manage known facts and reusable strategy memory.
- `remember.py`: manage known facts and reusable strategy memory; when a fact reaches the promotion threshold, sync it into the project-level `AGENTS.md` TraceMind Facts block.
- `hook.py`: create, list, or release pending hooks.

## Trigger Language

Use `memo.py` after important project changes, decisions, fixes, validations, or phase summaries.

Use `recall.py` for:

- "查历史"
- "召回"
- "回忆"
- "回顾"
- "以前"
- "之前"
- "昨天"
- "前天"
- "大前天"

When using `recall.py`, you MUST brainstorm multiple synonyms for your search terms to overcome strict SQLite matching (e.g., "按钮 按键 button"). Pass these synonyms as a single string.

Use `remember.py` for:

- "记住"
- "记住了"
- "记下来"
- "铁律"
- "避坑"
- "经验"
- "known fact"
- "known_facts"
- "策略记忆"
- "agent rule"

Use `hook.py` for:

- "hook"
- "挂起"
- "待办"
- "记住待办"
- "先记一下"
- "等待确认"
- "释放"
- "完成"

## Rules

- Do not store ordinary chatter.
- Store why something changed, not only what changed.
- Keep memo events separate from known facts.
- Known facts may be solidified into project rules; `recall.py` still returns only memo history.
- Use the current workspace root as `--root .` unless the user names a different root.
- On first use in a project, the LLM should bootstrap the environment by thoughtfully injecting the TraceMind Protocol block into the host-specific rules file (e.g., AGENTS.md), then run `init.py`.
- On first use in a project, the skill should also bootstrap `dev-log.md` so the human-readable log stays aligned with the database.
- Each memo add should refresh `dev-log.md` and append the same entry to `dev-log-archive/memo_archive.jsonl`.
- Promotion threshold for `AGENTS.md`: `after-action` evidence with `adopt_count >= 2` and `confidence >= 0.75`.
