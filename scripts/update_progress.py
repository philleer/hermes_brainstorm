#!/usr/bin/env python3
"""Scan Markdown checkboxes and rebuild the phone-friendly progress dashboard."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CST = timezone(timedelta(hours=8))

GITHUB = "https://github.com/philleer/hermes_brainstorm"
PAGES = "https://philleer.github.io/hermes_brainstorm"

TRACKS = [
    {
        "id": "ai-ml",
        "name": "AI / 机器学习",
        "files": [
            ("topics/ai-ml/quantization-learning-roadmap.md", "量化与部署路线"),
            ("topics/ai-ml/phase1-study-plan.md", "Phase 1 学习计划"),
            ("topics/ai-ml/phase1-knowledge-checklist.md", "Phase 1 知识清单"),
            ("topics/ai-ml/rlhf-quantization-guide.md", "RLHF + 混合精度"),
        ],
    },
    {
        "id": "cpp",
        "name": "C++ 工程",
        "files": [
            ("topics/cpp/design-patterns.md", "设计模式学习路径"),
            ("topics/cpp/poco-architecture.md", "POCO 架构"),
        ],
    },
    {
        "id": "inbox",
        "name": "Inbox 待整理",
        "files": [
            ("ideas/inbox/prompt-to-loop-engineering.md", "Prompt → Loop Engineering"),
        ],
    },
]

TASK_RE = re.compile(r"^[\t ]*[-*]\s+\[([ xX])\]\s+(.+)$")
PUNCH_RE = re.compile(r"^[ \t]*[□☑✓■]\s+(.+?)\s+\[([ xX])\]\s*$")


def strip_md(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_file(rel: str) -> list[dict]:
    path = ROOT / rel
    if not path.exists():
        return []
    items: list[dict] = []
    in_fence = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip().startswith("```"):
            in_fence = not in_fence
            continue
        m = TASK_RE.match(raw)
        if m:
            items.append(
                {
                    "done": m.group(1).lower() == "x",
                    "text": strip_md(m.group(2)),
                    "file": rel,
                }
            )
            continue
        if in_fence:
            p = PUNCH_RE.match(raw)
            if p:
                items.append(
                    {
                        "done": p.group(2).lower() == "x",
                        "text": strip_md(p.group(1)),
                        "file": rel,
                    }
                )
    return items


def pct(done: int, total: int) -> int:
    return 0 if total == 0 else round(100 * done / total)


def bar(done: int, total: int, width: int = 20) -> str:
    if total == 0:
        return "·" * width
    filled = round(width * done / total)
    return "█" * filled + "░" * (width - filled)


def collect() -> dict:
    tracks = []
    all_items: list[dict] = []
    for track in TRACKS:
        files = []
        track_items: list[dict] = []
        for rel, title in track["files"]:
            items = parse_file(rel)
            files.append(
                {
                    "path": rel,
                    "title": title,
                    "url": f"{GITHUB}/blob/main/{rel}",
                    "done": sum(1 for i in items if i["done"]),
                    "total": len(items),
                    "open": [i for i in items if not i["done"]],
                    "closed": [i for i in items if i["done"]],
                }
            )
            track_items.extend(items)
        tracks.append(
            {
                "id": track["id"],
                "name": track["name"],
                "files": files,
                "done": sum(1 for i in track_items if i["done"]),
                "total": len(track_items),
            }
        )
        all_items.extend(track_items)

    now = datetime.now(CST)
    done = sum(1 for i in all_items if i["done"])
    total = len(all_items)
    return {
        "generated_at": now.strftime("%Y-%m-%d %H:%M"),
        "timezone": "CST",
        "done": done,
        "total": total,
        "pct": pct(done, total),
        "open": total - done,
        "tracks": tracks,
        "inbox_files": len(list((ROOT / "ideas" / "inbox").glob("*.md")))
        if (ROOT / "ideas" / "inbox").exists()
        else 0,
    }


def render_progress_md(data: dict) -> str:
    lines = [
        "# 学习进度看板",
        "",
        f"> 手机端直接打开：[进度主页]({PAGES}) · 更新于 {data['generated_at']} CST",
        "",
        f"**总进度 {data['pct']}%**　{data['done']} / {data['total']} 已完成　剩余 {data['open']}　Inbox {data['inbox_files']} 条",
        "",
        "```",
        f"{bar(data['done'], data['total'], 28)}  {data['pct']}%",
        "```",
        "",
        "## 分轨进度",
        "",
        "| 主题 | 进度 | 完成 |",
        "|------|------|------|",
    ]
    for track in data["tracks"]:
        lines.append(
            f"| {track['name']} | `{bar(track['done'], track['total'])}` {pct(track['done'], track['total'])}% "
            f"| {track['done']}/{track['total']} |"
        )
    lines += ["", "## 明细", ""]
    for track in data["tracks"]:
        lines += [f"### {track['name']}", ""]
        for f in track["files"]:
            p = pct(f["done"], f["total"])
            lines.append(f"#### [{f['title']}]({f['url']}) — {f['done']}/{f['total']} ({p}%)")
            lines.append("")
            if f["total"] == 0:
                lines.append("_这篇还没有可勾选的任务。_")
                lines.append("")
                continue
            remaining = f["open"][:12]
            if remaining:
                for item in remaining:
                    lines.append(f"- [ ] {item['text']}")
                extra = len(f["open"]) - len(remaining)
                if extra > 0:
                    lines.append(f"- … 还有 {extra} 项，打开原文查看")
            else:
                lines.append("- [x] 本篇任务已全部完成")
            lines.append("")
    lines += [
        "---",
        "",
        "勾选笔记里的 `- [ ]` 后 `git push`，GitHub Action 会自动刷新这个看板。",
        "",
    ]
    return "\n".join(lines)


def render_html(data: dict) -> str:
    track_html = []
    for track in data["tracks"]:
        tp = pct(track["done"], track["total"])
        files_html = []
        for f in track["files"]:
            fp = pct(f["done"], f["total"])
            items = f["open"][:8]
            lis = "".join(
                f"<li>{escape(item['text'])}</li>" for item in items
            ) or ("<li class='muted'>暂无待办，或这篇还没有勾选任务</li>" if f["total"] == 0 else "<li class='ok'>本篇已完成</li>")
            extra = len(f["open"]) - len(items)
            more = f"<p class='more'>还有 {extra} 项</p>" if extra > 0 else ""
            files_html.append(
                f"""
<article class="file">
  <a class="file-head" href="{f['url']}">
    <span class="file-title">{escape(f['title'])}</span>
    <span class="file-stat">{f['done']}/{f['total']}</span>
  </a>
  <div class="meter"><span style="width:{fp}%"></span></div>
  <ul>{lis}</ul>
  {more}
</article>"""
            )
        track_html.append(
            f"""
<section class="track">
  <header>
    <h2>{escape(track['name'])}</h2>
    <span>{track['done']}/{track['total']} · {tp}%</span>
  </header>
  <div class="meter big"><span style="width:{tp}%"></span></div>
  {''.join(files_html)}
</section>"""
        )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#111827">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Hermes 进度">
  <title>学习进度 · hermes_brainstorm</title>
  <link rel="manifest" href="manifest.webmanifest">
  <style>
    :root {{
      --bg: #0b1220;
      --card: #152033;
      --line: #243049;
      --text: #e8eef9;
      --muted: #93a0b8;
      --accent: #5eead4;
      --warn: #fbbf24;
      --ok: #86efac;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; background: var(--bg); color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }}
    body {{ padding: calc(18px + env(safe-area-inset-top)) 16px calc(28px + env(safe-area-inset-bottom)); }}
    h1 {{ font-size: 1.35rem; margin: 0 0 4px; }}
    h2 {{ font-size: 1.05rem; margin: 0; }}
    .sub {{ color: var(--muted); font-size: 0.86rem; margin-bottom: 18px; }}
    .hero {{
      background: linear-gradient(160deg, #134e4a, #152033 55%);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 20px 18px 16px;
      margin-bottom: 16px;
    }}
    .pct {{ font-size: 3rem; font-weight: 730; letter-spacing: -0.04em; line-height: 1; color: var(--accent); }}
    .stats {{ display: flex; gap: 14px; margin-top: 12px; color: var(--muted); font-size: 0.9rem; }}
    .meter {{ height: 8px; background: #0b1220; border-radius: 99px; overflow: hidden; margin: 10px 0 12px; }}
    .meter.big {{ height: 10px; }}
    .meter span {{ display: block; height: 100%; background: linear-gradient(90deg, #2dd4bf, #a3e635); }}
    .track {{ background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 14px; margin-bottom: 14px; }}
    .track header {{ display: flex; justify-content: space-between; align-items: baseline; gap: 8px; color: var(--muted); }}
    .file {{ border-top: 1px solid var(--line); padding-top: 10px; margin-top: 10px; }}
    .file-head {{ display: flex; justify-content: space-between; gap: 8px; color: var(--text); text-decoration: none; }}
    .file-title {{ font-weight: 650; }}
    .file-stat {{ color: var(--muted); font-variant-numeric: tabular-nums; }}
    ul {{ margin: 8px 0 0; padding-left: 18px; color: var(--muted); font-size: 0.92rem; }}
    li {{ margin: 4px 0; }}
    .ok {{ color: var(--ok); }}
    .muted {{ color: var(--muted); }}
    .more {{ margin: 6px 0 0; color: var(--warn); font-size: 0.82rem; }}
    .hint {{ color: var(--muted); font-size: 0.82rem; line-height: 1.5; }}
    a.btn {{ display: inline-block; margin-top: 10px; color: var(--accent); }}
  </style>
</head>
<body>
  <div class="hero">
    <h1>hermes_brainstorm</h1>
    <p class="sub">学习进度 · {escape(data['generated_at'])} CST</p>
    <div class="pct">{data['pct']}%</div>
    <div class="meter big"><span style="width:{data['pct']}%"></span></div>
    <div class="stats">
      <span>已完成 {data['done']}</span>
      <span>剩余 {data['open']}</span>
      <span>Inbox {data['inbox_files']}</span>
    </div>
  </div>
  {''.join(track_html)}
  <p class="hint">
    把这个页面添加到手机主屏幕，即可随时查看进度。<br>
    在笔记中勾选任务并 push 后，看板会自动刷新。
    <br><a class="btn" href="{GITHUB}">打开 GitHub 仓库</a>
  </p>
</body>
</html>
"""


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main() -> None:
    data = collect()
    DOCS.mkdir(parents=True, exist_ok=True)
    (ROOT / "PROGRESS.md").write_text(render_progress_md(data), encoding="utf-8")
    (DOCS / "index.html").write_text(render_html(data), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "manifest.webmanifest").write_text(
        json.dumps(
            {
                "name": "hermes_brainstorm 进度",
                "short_name": "学习进度",
                "start_url": "./",
                "display": "standalone",
                "background_color": "#0b1220",
                "theme_color": "#111827",
                "lang": "zh-CN",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"progress {data['done']}/{data['total']} ({data['pct']}%) "
        f"-> PROGRESS.md + docs/index.html"
    )


if __name__ == "__main__":
    main()
