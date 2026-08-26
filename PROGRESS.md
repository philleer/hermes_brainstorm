# 学习进度看板

> 手机端直接打开：[进度主页](https://philleer.github.io/hermes_brainstorm) · 更新于 2026-08-26 17:36 CST

**总进度 0%**　0 / 79 已完成　剩余 79　Inbox 1 条

```
░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0%
```

## 分轨进度

| 主题 | 进度 | 完成 |
|------|------|------|
| AI / 机器学习 | `░░░░░░░░░░░░░░░░░░░░` 0% | 0/36 |
| C++ 工程 | `░░░░░░░░░░░░░░░░░░░░` 0% | 0/30 |
| Inbox 待整理 | `░░░░░░░░░░░░░░░░░░░░` 0% | 0/13 |

## 明细

### AI / 机器学习

#### [量化与部署路线](https://github.com/philleer/hermes_brainstorm/blob/main/topics/ai-ml/quantization-learning-roadmap.md) — 0/15 (0%)

- [ ] 能手写出对称量化/非对称量化的公式
- [ ] 能解释为什么 B-bit 量化的理论 SNR ≈ 6.02B + 1.76 dB
- [ ] 能用 numpy 实现一个 toy quantizer
- [ ] 能手动画出 PTQ 的 calibration → 量化流程
- [ ] 能解释 per-channel 为什么比 per-tensor 好
- [ ] 能跑通一个 ResNet/MobileNet 的 INT8 量化
- [ ] 能量化前后精度差异 < 2%
- [ ] 能解释为什么 Transformer 的激活值量化比 CNN 难
- [ ] 理解 LLM.int8() 的混合精度策略
- [ ] 能用 bitsandbytes 加载 4-bit/8-bit 模型
- [ ] 了解 GPTQ、AWQ、SmoothQuant 的核心区别
- [ ] 能用一种工具链完成 ONNX → 芯片格式的转换
- … 还有 3 项，打开原文查看

#### [Phase 1 学习计划](https://github.com/philleer/hermes_brainstorm/blob/main/topics/ai-ml/phase1-study-plan.md) — 0/12 (0%)

- [ ] Day 1 (周一) — 浮点数二进制表示
- [ ] Day 2 (周二) — 浮点数精度与范围
- [ ] Day 3 (周三) — 量化公式推导
- [ ] Day 4 (周四) — 量化误差分析
- [ ] Day 5 (周五) — Per-tensor vs Per-channel
- [ ] Day 6 (周六) — 复习 + Cheat Sheet
- [ ] Day 7 (周日) — PyTorch 量化基础
- [ ] Day 8 (周一) — PTQ 完整流程
- [ ] Day 9 (周二) — FakeQuantize 深入
- [ ] Day 10(周三) — 敏感度可视化
- [ ] Day 11(周四) — 综合实验
- [ ] Day 12(周五) — 总结 + Phase 2 衔接

#### [Phase 1 知识清单](https://github.com/philleer/hermes_brainstorm/blob/main/topics/ai-ml/phase1-knowledge-checklist.md) — 0/9 (0%)

- [ ] Machine Epsilon（机器精度）：使 1.0 + ε ≠ 1.0 的最小 ε
- [ ] ULP (Unit in the Last Place)：两个相邻浮点数之间的间距
- [ ] Subnormal Number（非规格化数）：比最小规格化数更小的数
- [ ] 为什么 0.1 + 0.2 ≠ 0.3：0.1 和 0.2 在二进制中是无限循环小数，存储时已被截断
- [ ] 能用 numpy 手写对称/非对称量化函数（不看参考资料）
- [ ] 能解析一个 FP32 的二进制表示（sign/exponent/mantissa）
- [ ] 能用 PyTorch 跑通 dynamic quantization
- [ ] 能画出量化误差的分布直方图，验证 SNR 公式
- [ ] 能解释 per-channel 为什么比 per-tensor 好，并给出量化误差数据

#### [RLHF + 混合精度](https://github.com/philleer/hermes_brainstorm/blob/main/topics/ai-ml/rlhf-quantization-guide.md) — 0/0 (0%)

_这篇还没有可勾选的任务。_

### C++ 工程

#### [设计模式学习路径](https://github.com/philleer/hermes_brainstorm/blob/main/topics/cpp/design-patterns.md) — 0/25 (0%)

- [ ] Autoware — Component 机制 & 进程内通信
- [ ] Autoware — Lifecycle Nodes（状态模式）
- [ ] Autoware — Behavior Tree（组合模式）
- [ ] Apollo — CyberRT 无锁队列 & 协程调度
- [ ] Apollo — 插件机制（工厂模式 + 宏反射）
- [ ] Apollo — 规划/控制 Pipeline（策略模式）
- [ ] Folly — FBString 动态策略模式
- [ ] Folly — MPMCQueue 无锁队列 & 缓存行对齐
- [ ] Folly — Function 多态 + 小对象优化
- [ ] Poco — NotificationCenter 观察者模式
- [ ] Poco — ClassLoader 动态插件加载
- [ ] Poco — ThreadPool 命令模式 + 工作者模式
- … 还有 13 项，打开原文查看

#### [POCO 架构](https://github.com/philleer/hermes_brainstorm/blob/main/topics/cpp/poco-architecture.md) — 0/5 (0%)

- [ ] 用 Poco::NotificationCenter 实现一个简单的消息总线
- [ ] 基于 Poco::Net::SocketReactor 写一个简易聊天服务器
- [ ] 用 Poco::Data 实现一个支持多数据库后端的 DAO 层
- [ ] 基于 Poco::Util::Application 搭建一个带插件机制的服务框架
- [ ] 模仿 Poco 的 *_UNIX.cpp / *_WIN32.cpp 模式，写一个跨平台文件监控器

### Inbox 待整理

#### [Prompt → Loop Engineering](https://github.com/philleer/hermes_brainstorm/blob/main/ideas/inbox/prompt-to-loop-engineering.md) — 0/13 (0%)

- [ ] Anthropic: "Harness design for long-running application development" (2026-03-24)
- [ ] Anthropic: "How we contain Claude across products" (2026-05-25)
- [ ] Anthropic: "Scaling Managed Agents: Decoupling the brain from the hands" (2026-04-08)
- [ ] Lilian Weng: "LLM Powered Autonomous Agents" (lilianweng.github.io)
- [ ] 搜索 "context engineering" 相关论文
- [ ] 阅读 Anthropic 工程博客相关文章
- [ ] 整理每个阶段的代表性论文和工具
- [ ] 对比不同 Agent 框架（LangChain、AutoGPT、Hermes）在这四个维度的设计
- [ ] 写一篇总结文章归入 topics/ai-ml/
- [ ] 收集 4 篇核心论文/博客的链接
- [ ] 找一张这四阶段关系的示意图或自己画
- [ ] 整理成学习 roadmap
- … 还有 1 项，打开原文查看

---

勾选笔记里的 `- [ ]` 后 `git push`，GitHub Action 会自动刷新这个看板。
