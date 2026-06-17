# TraceMind

[English](README_en.md) | [中文版](README.md)

**TraceMind** 是一个零配置、面向 AI 代码助手（Cursor, Windsurf, Claude Code, Antigravity 等）的**项目级局部记忆引擎**。它完全基于 Python 原生脚本构建，无需部署复杂的 MCP 服务，即可赋予 AI 持久化的项目记忆能力。

## ✨ 核心特性

- **零配置插拔即用**：无需部署服务端。只需将本 Skill 放入目录，即可在项目根目录自动维护 SQLite 记忆库。
- **时间线与备忘录**：在完成代码或文档修改后，自动记录备忘，并生成直观的 HTML 格式项目开发时间线。
- **智能模糊召回**：内置“宽进严出”算法，即便 AI 遗忘确切关键词，也能通过近义词网络精准召回历史采坑记录。
- **三步反思工作流 (3-Step Reflection)**：在解决复杂 Bug 或完成重要阶段任务后，AI 会自动触发“记录流水账 -> 跨表翻找历史大坑 -> 提炼新经验”闭环，极大地节省 Token。
- **经验极速固化**：当某条候选经验被二次验证有效，其置信度将瞬间跃升，并自动**硬编码**到您的 IDE 系统规则（如 `.cursor/rules` 或 `AGENTS.md`）中，永远不再犯同样的错。

## 📦 安装说明

1. 前往本仓库的 [Releases 页面](https://github.com/halflifezyf2680/TraceMind-Skill/releases) 下载最新的 `tracemind-skill-vX.X.X.zip`。
2. 将压缩包解压后，得到一个干净的 `tracemind` 文件夹。
3. 将该文件夹放置到您的 AI IDE 或 Agent 的全局技能（Skills）目录下（例如 `~/.gemini/config/skills/` 或您自定义的技能挂载目录）。

## 🚀 使用指南

### 启动与部署
在您的任意代码项目中，首次呼出 AI 时，只需在对话框中唤起该技能（取决于您的客户端支持 `/` 还是 `@` 语法）：
> `/tracemind` 或 `@tracemind`

AI 会自动挂载该技能，阅读内置协议，并将工作流守则写入您当前项目的规则文件中（如 `AGENTS.md`），随后自动初始化数据库。

### 日常交互
您无需记住复杂的命令，直接用自然语言与 AI 沟通即可触发记忆机制：
- **"记住这个坑" / "设为铁律"**：AI 会立刻将其写入候选经验池。
- **"这几天我们都做了什么？"**：AI 会帮您调用脚本，渲染并打开一个精美的项目时间线 HTML 页面。
- **"把手头的工作挂起"**：AI 会记录一个 Pending Hook，方便您明天继续跟进。

*详细的底层 API 和协议设计，请参阅 [`SKILL.md`](./SKILL.md) 与 [`references/tracemind-protocol.md`](./references/tracemind-protocol.md)。*

## 📄 开源协议

本项目采用 [MIT License](./LICENSE) 开源协议。
