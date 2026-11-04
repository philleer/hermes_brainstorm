# DECISIONS

> 追加式决策日志。只记「定了什么」和「为什么」；不要改写旧条目，新决策往下追加。

## 2026-10-20 — 仓库内摘要交接，不同步全文聊天

- **Decision:** 跨 App 连续性采用仓库根目录 `CONTEXT.md` + `DECISIONS.md` + `sessions/` 摘要；不建各厂商 chat 统一同步器；第一版不用向量库。
- **Why:** 各 App session 封闭且格式不一；真正可交接的是状态、决策与下一步。Markdown + Git 已与本仓工作流一致，换 App 即可冷启动。
- **Rejected:** 全量 transcript 同步；把所有项目 CONTEXT 集中存进 hermes_brainstorm。
- **Source:** cursor
