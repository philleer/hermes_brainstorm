---
date: 2026-06-18
tags: [ai-engineering, prompt-engineering, agent]
status: inbox
---

# Prompt Engineering → Context Engineering → Harness Engineering → Loop Engineering 发展历程调研

## 灵感来源
- Anthropic 工程博客近期频繁出现 "harness" 概念（harness design for long-running apps）
- 注意到 AI 工程化从"怎么写 prompt"逐步演进到"怎么设计 Agent 运行环境"
- 想系统梳理这条演进路线

## 四个阶段初步理解

### 1. Prompt Engineering（提示工程）
- 关注点：如何写出更好的 prompt
- 代表技术：few-shot、chain-of-thought、role prompting
- 局限：单轮对话，上下文窗口有限

### 2. Context Engineering（上下文工程）
- 关注点：如何管理和利用上下文窗口
- 代表技术：RAG、上下文压缩、记忆管理、长上下文模型
- 标志性事件：Claude 200K、Gemini 1M+ token 上下文

### 3. Harness Engineering（托架工程）
- 关注点：如何为 Agent 设计运行环境和约束
- 代表技术：sandboxing、tool integration、permission models、containerization
- Anthropic 博客：harness design for long-running apps, how we contain Claude

### 4. Loop Engineering（循环工程）
- 关注点：Agent 自主运行的反馈循环
- 代表技术：self-reflection、multi-agent orchestration、continuous learning loops
- 相关：AutoGPT 类自主 agent、Hermes 的 cron + delegation

## 调研方向

### 论文/博客
- [ ] Anthropic: "Harness design for long-running application development" (2026-03-24)
- [ ] Anthropic: "How we contain Claude across products" (2026-05-25)
- [ ] Anthropic: "Scaling Managed Agents: Decoupling the brain from the hands" (2026-04-08)
- [ ] Lilian Weng: "LLM Powered Autonomous Agents" (lilianweng.github.io)
- [ ] 搜索 "context engineering" 相关论文

### 关键问题
- prompt → context 的转折点在哪里？
- harness 和 context 的关系是什么？（harness 管理 context 的边界？）
- loop 是 harness 的必然延伸还是独立阶段？
- 这四个阶段是线性演进还是并存互补？

### 学习路径
- [ ] 阅读 Anthropic 工程博客相关文章
- [ ] 整理每个阶段的代表性论文和工具
- [ ] 对比不同 Agent 框架（LangChain、AutoGPT、Hermes）在这四个维度的设计
- [ ] 写一篇总结文章归入 topics/ai-ml/

## 下一步
- [ ] 收集 4 篇核心论文/博客的链接
- [ ] 找一张这四阶段关系的示意图或自己画
- [ ] 整理成学习 roadmap
