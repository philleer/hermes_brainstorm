# Session: 2026-11-04 — realtime vision PC-first

- **Source:** cursor
- **Repo:** hermes_brainstorm
- **Updated CONTEXT?** no（本仓 Goal 仍是跨 App Agent 记忆协议；本主题进 `ideas/inbox/`，避免覆盖）

## Goal

明确 iPhone 实时视觉+3DGS 需求在无 Mac 条件下的开发路径，并锁定 PC 验证阶段的技术选型。

## Outcome

- 确认：无 Mac 则不做原生 iOS；Xcode 不可装手机；Developer 账号可延后。
- 锁定分辨率、Depth Anything、H.265/MOV、gsplat；**Windows 部署量化 / Linux 运行时**；GPU **A40 + 1080 Ti**。
- 写入并更新 `ideas/inbox/realtime-vision-3dgs-pc-first.md`。

## Changes

- `ideas/inbox/realtime-vision-3dgs-pc-first.md`（新增）
- `sessions/2026-11-04-realtime-vision-pc-first.md`（本文件）

## Open questions

- Depth Anything 变体在 A40 vs 1080 Ti 的档位
- 运行时 ORT vs TensorRT（TRT 需按卡分别建 engine）
- 1080 Ti 的 CUDA/PyTorch 版本上限
- gsplat 位姿从何而来

## Takeaways

1. 1080p 显示与落盘，YOLO 用 960×540，结果 ×2 映回。
2. 3DGS 对齐 gsplat，Phase 0 只做离线重建。
3. Windows 出 artifacts，Linux 只跑验证；A40 主力量化，1080 Ti 做降级 profile。
