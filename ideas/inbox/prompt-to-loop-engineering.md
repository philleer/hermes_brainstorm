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

## 核心思考

### 主要关注什么？

表面上是四个阶段的演进史，**本质上关注的是 AI 工程化从"手艺"到"工程学科"的范式转变**：

- Prompt Engineering 像是"驭马术"——你在和一匹聪明的马对话，技巧全在措辞
- Context Engineering 是给马装了更大的车厢——你能装更多东西了，但依然是一趟一趟跑
- **Harness Engineering 是分水岭**——你不再只是骑马，你开始设计马车的整套缰绳、刹车、护栏系统。Agent 由"被调用"变成"被托管"
- Loop Engineering 是让马车自己跑——你设定目的地，它自己规划路线、修正偏差、报告进度

**核心洞察**：每上升一个阶段，人在系统中的角色就退后一步——从操作者 → 管理者 → 设计者 → 监督者。

### 为什么有用？

1. **框架价值**：给零散的 AI 技术（RAG、Agent、memory、sandbox）一个统一的演进坐标系，帮助判断某项技术处于哪个阶段、天花板在哪里
2. **职业判断**：当所有人还在卷 Prompt Engineering 时，Harness/Loop 方向的工程师极度稀缺。这是一条相对蓝海的技能路线
3. **选型决策**：选工具/框架时，可以快速判断它在哪个阶段——比如 LangChain 本质是 context engineering，AutoGPT 是 loop engineering 的早期尝试，Hermes 是目前少有的同时覆盖四个阶段的系统

### 对日常工作的帮助？

**直接相关**——你现在的工作恰好横跨四个阶段：

| 阶段 | 你的日常实践 |
|------|-------------|
| Prompt | 每天和 Hermes 对话，写 skill 指令 |
| Context | Hermes 的 memory、skills 加载、session 管理 |
| Harness | Hermes 的 sandbox、delegation、tool integration、cron 调度 |
| Loop | Hermes 的 cron job 自主运行、多 agent 编排、你的 "话题追踪" 系统 |

**两个具体应用方向**：

1. **把 Hermes 当实验场**：你正在用的 skill 系统、cron job、delegate_task 本身就是 loop engineering 的实践。理解这个框架后，可以更有意识地设计 Hermes 的自主工作流——不只是"让 AI 帮我干活"，而是"设计一个 AI 能自己跑起来的系统"
2. **边缘部署的延伸**：你做的 YOLO 模型部署到 X5/X6 芯片，本质上也是 Harness Engineering——模型是"大脑"，芯片上的 runtime、内存管理、推理管线是"托架"。这套思维可以直接迁移到端侧 Agent 的设计上

### 一句话总结

> Prompt Engineering 解决"AI 能做什么"，Context Engineering 解决"AI 能记住什么"，Harness Engineering 解决"AI 能安全地做什么"，Loop Engineering 解决"AI 能自己持续做什么"——你不是在学四个技术，而是在理解一个完整的 AI 系统设计方法论。

## 下一步
- [ ] 收集 4 篇核心论文/博客的链接
- [ ] 找一张这四阶段关系的示意图或自己画
- [ ] 整理成学习 roadmap
- [ ] 用这个框架审视自己的 Hermes 工作流，看看哪些可以升级到 higher loop
