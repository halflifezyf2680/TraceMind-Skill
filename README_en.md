# TraceMind

[English](README_en.md) | [中文版](README.md)

**TraceMind** is a zero-config, project-level local memory engine for AI coding assistants (Cursor, Windsurf, Claude Code, Antigravity, etc.). Built entirely on native Python scripts, it gives your AI persistent project memory without the need to deploy complex MCP services.

## ✨ Features

- **Zero-config & Plug-and-Play**: No servers to deploy. Drop the skill into your directory, and it autonomously manages an SQLite memory bank in your project root.
- **Timeline & Memos**: Records a memo after any code or document change, rendering a beautiful HTML timeline of your project's development history.
- **Smart Fuzzy Recall**: Uses a "Broad-in, Strict-out" algorithm to flawlessly retrieve history even if the AI misremembers exact keywords.
- **3-Step Reflection Flow**: After solving complex bugs, the AI triggers a "Record history -> Cross-reference pitfalls -> Extract new rules" loop, saving Context Tokens while evolving its knowledge.
- **Fast Experience Evolution**: Once a candidate lesson is validated, it immediately breaches the confidence threshold and is automatically hardcoded into your IDE's system rules (e.g., `.cursor/rules` or `AGENTS.md`).

## 📦 Installation

1. Go to the [Releases page](https://github.com/halflifezyf2680/TraceMind-Skill/releases) and download the latest `tracemind-skill-vX.X.X.zip`.
2. Extract the archive to get a clean `tracemind` folder.
3. Place this folder into your AI IDE or Agent's global skills directory (e.g., `~/.gemini/config/skills/` or your custom skill mount directory).

## 🚀 Usage

### Initialization & Deployment
In any code project, when opening your AI chat for the first time, simply invoke the skill (using `/` or `@` depending on your client):
> `/tracemind` or `@tracemind`

The AI will automatically mount the skill, read the built-in protocol, write the workflow rules to your project's local rule file (e.g., `AGENTS.md`), and initialize the database.

### Daily Interaction
You don't need to memorize complex commands. Just talk to your AI using natural language:
- **"Remember this pitfall" / "Make this a strict rule"**: The AI will immediately log it into the candidate memory pool.
- **"Open timeline"**: The AI will render and open a beautiful project timeline HTML page.
- **"Summarize current task into a todo, I'm switching to Cursor"** or **"I have an idea for a feature, log it"**: The AI will create a cross-session Pending Hook, allowing you to seamlessly resume context anywhere.

*For detailed underlying APIs and protocol designs, please refer to [`SKILL.md`](./SKILL.md) and [`references/tracemind-protocol.md`](./references/tracemind-protocol.md).*

## 📄 License

This project is licensed under the [MIT License](./LICENSE).
