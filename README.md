# 🧠 hermes_brainstorm

> 日常想法记录 & AI 头脑风暴 · 跨平台同步的知识仓库

一个极简的个人知识仓库，用于记录日常灵感、与 AI 的深度对话，以及结构化的头脑风暴内容。所有内容以 Markdown 格式存储，通过 Git 实现跨平台同步。

---

## ✨ 核心用途

- **日常灵感捕获** — 随时随地记录一闪而过的想法，不遗漏任何创意火花
- **AI 头脑风暴存档** — 保存与 AI Agent（如 Hermes）的深度对话，提炼有价值的讨论
- **知识结构化** — 将零散的想法逐步整理为可检索、可复用的知识卡片
- **跨平台同步** — 基于 Git 的同步机制，在 Windows / macOS / Linux 之间无缝切换

---

## 📁 目录结构

```
hermes_brainstorm/
├── README.md
├── PROGRESS.md               # 进度摘要（GitHub Mobile 可看）
├── docs/                     # 手机端进度看板（GitHub Pages）
├── scripts/update_progress.py
├── ideas/
│   └── inbox/                # 待整理的原始想法（免压区，先记下来再说）
├── topics/                   # 按主题归档的知识卡片
│   ├── ai-ml/                # AI / 机器学习
│   ├── cpp/                  # C++ 相关
│   └── ...
└── .github/workflows/        # push 后自动刷新看板
```

**两阶段工作流**：inbox 快速捕获 → 整理后归入对应 topics 子目录。

---

## 🚀 快速开始

### 克隆仓库

```bash
git clone https://github.com/philleer/hermes_brainstorm.git
cd hermes_brainstorm
```

### 记录一条想法

在 `ideas/inbox/` 下新建一个 Markdown 文件：

```markdown
# 用边缘设备做实时语音翻译

## 灵感来源
- 看到 Horizon X6 的 NPU 算力

## 核心想法
- 端侧 ASR + 端侧翻译，不依赖云端

## 下一步
- [ ] 调研 X6 上的语音模型支持
```

### 整理归档

定期把 inbox 里的内容归入 `topics/` 对应子目录，如果话题跨领域就放一个主目录，用标签关联。

---

## 📱 手机端监控进度

打开 **[学习进度看板](https://philleer.github.io/hermes_brainstorm/)**，Safari / Chrome 里选「添加到主屏幕」，即可随时查看各主题完成度。

| 场景 | 操作 |
|------|------|
| 手机看进度 | 打开看板，或 GitHub Mobile 看 [PROGRESS.md](PROGRESS.md) |
| 勾选完成项 | 在对应笔记里把 `- [ ]` 改成 `- [x]`，然后 push |
| 自动刷新 | 每次 push 到 `main`，GitHub Action 会重算进度并更新看板 |

本地预览看板：

```bash
python3 scripts/update_progress.py
```

---

## 🔄 跨平台同步

```bash
git pull                    # 拉取最新内容
# ... 编辑 / 记录 ...
git add . && git commit -m "add: 新的灵感记录"
git push                    # 推送到远程
```

| 场景 | 操作 |
|------|------|
| 手机端快速记录 | GitHub Mobile 或 Working Copy |
| 桌面端深度整理 | VS Code / Obsidian 打开仓库目录 |
| AI 对话存档 | 手动创建 Markdown 存入 topics |

> 💡 配合 [Obsidian](https://obsidian.md) 打开本仓库目录，可获得双向链接、图谱视图等高级功能。

---

## 📌 使用原则

1. **先记下来，再整理** — inbox 是免压区域，任何想法都可以先扔进去
2. **定期归档** — 建议每周清理一次 inbox，把内容归入 topics
3. **建立关联** — 善用标签和双向链接，让知识产生复利效应
4. **保持纯文本** — Markdown 是永恒的，不依赖任何专有格式

---

## 📄 License

MIT © phillee

---

*"The faintest ink is more powerful than the strongest memory." — 好记性不如烂笔头*