# 🧠 hermes_brainstorm

> 日常想法记录 & AI 头脑风暴 · 跨平台同步的知识仓库

一个轻量级的个人知识管理系统，用于记录日常灵感、与 AI 的深度对话，以及结构化的头脑风暴内容。所有内容以 Markdown 格式存储，配合 Python 工具链实现自动化管理，通过 Git 实现跨平台无缝同步。

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
├── README.md                 # 本文件
├── ideas/                    # 日常灵感碎片
│   ├── inbox/                # 待整理的原始想法（快速记录）
│   └── processed/            # 已整理归档的想法
├── sessions/                 # AI 头脑风暴会话记录
│   └── YYYY-MM/              # 按月归档
│       └── 2025-06-15-xxx.md
├── topics/                   # 按主题组织的知识卡片
│   ├── ai-ml/                # AI / 机器学习相关
│   ├── edge-computing/       # 边缘计算
│   └── ...
├── scripts/                  # Python 工具脚本
│   ├── new_idea.py           # 快速创建灵感记录
│   ├── archive.py            # 归档整理脚本
│   └── generate_index.py     # 生成索引页面
├── templates/                # 模板文件
│   ├── idea.md               # 灵感记录模板
│   └── session.md            # 头脑风暴会话模板
└── .gitignore
```

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/<your-username>/hermes_brainstorm.git
cd hermes_brainstorm
```

### 2. 快速记录一条想法

```bash
python scripts/new_idea.py "用边缘设备做实时语音翻译"
```

这会在 `ideas/inbox/` 下生成一个带时间戳的 Markdown 文件，自动填入模板。

### 3. 归档整理

```bash
python scripts/archive.py
```

将 `inbox` 中的想法按照内容分类，归档到 `ideas/processed/` 或相应的 `topics/` 目录。

### 4. 生成索引

```bash
python scripts/generate_index.py
```

自动扫描所有内容，生成一份可浏览的索引页面，方便回顾。

---

## 📝 内容模板

### 灵感记录 (`templates/idea.md`)

```markdown
---
date: {{date}}
tags: []
status: inbox
---

# {{title}}

## 灵感来源
- 

## 核心想法


## 相关链接
- 

## 下一步
- [ ] 深入调研
- [ ] 关联已有知识
```

### AI 会话记录 (`templates/session.md`)

```markdown
---
date: {{date}}
model: {{model}}
tags: []
---

# {{title}}

## 对话背景


## 核心观点


## AI 的洞察


## 我的反思


## 行动项
- [ ] 
```

---

## 🔄 跨平台同步

本仓库设计为纯文本 + Git 的同步方案，不依赖任何云服务：

```bash
# 在任意设备上
git pull                    # 拉取最新内容
# ... 编辑 / 记录 ...
git add . && git commit -m "add: 新的灵感记录"
git push                    # 推送到远程
```

### 推荐工作流

| 场景 | 操作 |
|------|------|
| 手机端快速记录 | 使用 GitHub Mobile 或 Working Copy 编辑 |
| 桌面端深度整理 | 本地 Clone 后用 VS Code / Obsidian 打开 |
| 与 AI 对话存档 | 对话结束后跑 `new_idea.py` 或手动创建 session |

> 💡 配合 [Obsidian](https://obsidian.md) 打开本仓库目录，可获得双向链接、图谱视图等高级功能。

---

## 🛠️ Python 环境

```bash
# 推荐使用 uv 管理依赖
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

依赖极简，仅需 Python 3.10+ 标准库即可运行核心脚本。

---

## 📌 使用原则

1. **先记下来，再整理** — inbox 是免压区域，任何想法都可以先扔进去
2. **定期归档** — 建议每周跑一次 `archive.py`，保持 inbox 清爽
3. **建立关联** — 善用标签和双向链接，让知识产生复利效应
4. **保持纯文本** — Markdown 是永恒的，不依赖任何专有格式

---

## 📄 License

MIT © [your-name]

---

*"The faintest ink is more powerful than the strongest memory." — 好记性不如烂笔头*