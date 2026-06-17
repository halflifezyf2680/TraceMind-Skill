# TraceMind

[English](README_en.md) | [中文版](README.md)

**TraceMind** 是一个以 Skill（技能）形式进行部署和挂载的项目级局部记忆引擎。它完全基于纯 Python 脚本驱动，能在**零复杂配置、零 MCP（模型上下文协议）服务依赖**的情况下，为目前主流的 AI 代码助手（如 Cursor, Windsurf, Claude Code, Antigravity, OpenCode 等）赋予持久化的项目记忆能力——包括开发事件时间线、经验法则沉淀、待办任务挂起以及策略记录。

## 核心特性

- **零配置本地存储**：在您的项目根目录下自动初始化并维护 `.mpm-data/mcp_memory.db` SQLite 数据库，插拔即用。
- **时间线与备忘录**：在完成代码或文档的修改后即可记录备忘 (`memo.py`)，并能直接渲染出精美直观的 HTML 格式开发时间线 (`timeline.py`)。
- **智能模糊召回**：“宽进严出”算法 (`recall.py`)。即使 AI Agent 记错了几个关键词，也能通过近义词网络兜底，并在结果呈现时执行极高的精度过滤。
- **三步反思工作流 (3-Step Reflection)**：在处理完复杂的顽固 BUG 或阶段性任务后，AI 会自动触发“记录流水账 -> 跨表翻找历史大坑 -> 提纯提炼经验”的 3 步闭环，在最节省 Context Token 的情况下，实现项目知识的自动升维。
- **经验沉淀与极速固化 (Fast Evolution)**：通过 `remember.py` 记录项目中的避坑指南与铁律。我们优化了内部算法：当某条候选经验被二次验证有效后，其置信度将瞬间跃升，自动被**写回并固化**到您当前 IDE 的系统规则文件（如 `AGENTS.md` 或 `.cursor/rules/tracemind.mdc`）中，形成完美闭环。
- **任务挂起**：在工作因某些原因被阻塞或需要等待确认时，随时挂起并管理待办任务 (`hook.py`)。

## 架构哲学

TraceMind 遵循了极其克制且解耦的架构设计：

1. **大模型认知层**：大模型（AI Agent）自己负责阅读参考文档 `references/rules-create.md`，然后发挥它的聪明才智，安全地将协议追加到您项目中已有的各类 `.md` 或 `.mdc` 规则文件中。绝对不破坏您已有的 YAML Frontmatter 格式。
2. **底层脚本执行层**：枯燥的 SQLite 增删改查、HTML 时间线渲染、日志快照导出，则全部由稳定可控的 Python 原生标准库脚本完成。

## 使用方法

详细的 AI 挂载规则、触发动作词汇表以及内部运行协议，请参考：
- [`SKILL.md`](./SKILL.md) （供 AI 挂载识别的技能描述文件）
- [`references/tracemind-protocol.md`](./references/tracemind-protocol.md) （核心协议说明书）
