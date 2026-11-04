---
date: 2026-11-04
tags: [cv, yolo, depth-anything, 3dgs, gsplat, ios, windows, wsl]
status: inbox
---

# 实时场景理解 + 3DGS（PC-Windows/WSL 先验证）

## 目标产品形态（远期）

iPhone 实时浏览：人脸检测/打码、物体分割、单目深度、3DGS 建模与渲染、多层结果录制；自用验证后再 App Store。

## 已锁定选型（2026-11-04）

| 项 | 决定 |
|----|------|
| 原图 / 预览 / 合成基准 | 1920×1080 |
| YOLO 人脸 DET + 物体 SEG 输入 | 960×540（同 16:9，结果 ×2 映回 1080p） |
| 深度 | Depth Anything（具体变体/权重待 Phase 0 定） |
| 录制 | 优先 **H.265 + MOV** |
| 3DGS | 先对齐 **gsplat** 方案（非实时优先：录段→重建→查看） |
| 验证平台 | **先 PC**；暂不投入 Mac/iOS |
| 主机分工 | **Windows：部署 + 量化**；**Linux：运行时验证** |
| GPU | **A40**（主量化/高吞吐）+ **RTX 1080 Ti**（兼容与降级验证） |
| 账号 | Apple Developer 延后到有可装包需求 |
| iOS 模型格式（远期） | **Core ML**（`.mlpackage` / ML Program）；Windows 的 ONNX/TRT **不能**直接上手机，需再转换或从 PyTorch 另导 |

## 主机与 GPU 分工

```
Windows                    Linux
─────────────────          ─────────────────
导出 ONNX / TensorRT       加载已导出引擎或 ONNX
PTQ / 校准 / 量化实验      端到端管线：采集→推理→合成→录像
打包权重与配置产物  ──►    运行时验证、FPS/精度回归
gsplat 训练可放 A40        gsplat 渲染/回放也可在 Linux
```

| GPU | 角色 | 注意 |
|-----|------|------|
| **A40**（48GB, Ampere） | 量化校准、多模型并行、Depth 较大变体、gsplat 训练主卡 | TensorRT / FP16 / INT8 主力目标 |
| **1080 Ti**（11GB, Pascal sm_61） | 「老卡也能跑」基线；卡分辨率与跳帧下限 | 无现代 Tensor Core；新版 PyTorch/CUDA 可能已不支持或需旧栈；INT8 TensorRT 收益有限，优先 **FP16/FP32 + 更小模型**；显存紧，DET+SEG+Depth 同时驻留要控 batch=1 与模型体量 |

**产物约定（建议）：** Windows 产出版本化目录，例如 `artifacts/yolo_det_540_fp16/`、`artifacts/depth_anything_v2_s_540/`（含 onnx/engine、校准信息、输入尺寸、预处理均值方差）；Linux **只消费 artifacts**，不在验证机上现场量化，避免两套数字对不上。

## Phase 0 — PC 验证范围（建议）

1. **相机/视频源**：USB 摄像头或本地 1080p 视频文件循环。
2. **共享帧总线**：读入 1080p → 生成 960×540 推理帧 → 多消费者订阅。
3. **YOLO26-DET（人脸）**：540p 推理 → 框映回 1080p → ROI 打码。
4. **YOLO26-SEG**：540p 推理 → 框/掩码/类别/置信度叠到 1080p。
5. **Depth Anything**：建议默认输入 ≤960×540（可再降到 640×360 做 A/B）→ 伪彩面板。
6. **录制**：1080p 合成画面 H.265/MOV；旁路可选存 JSON/掩码/深度（时间戳对齐）。
7. **3DGS / gsplat**：离线路径——选关键帧或短 clip → 按 gsplat 流程重建 → 独立窗口查看；**不**进实时热路径。

## 非目标（Phase 0）

- iOS / Core ML / App Store
- 实时流式 3DGS 训练
- 四模型每帧全开且保 30 FPS（先测得数，再定跳帧策略）

## 建议目录（新独立仓库时）

```
vision_pc_proto/
  capture/          # 相机与视频（主路径在 Linux）
  infer/            # 运行时加载 artifacts
  compose/          # 1080p 叠加与打码
  record/           # H.265 MOV
  gsplat_offline/   # 导出关键帧 + gsplat 脚本
  deploy/           # Windows：导出、量化、校准（可子树或独立 repo）
  artifacts/        # 版本化模型产物（Git LFS 或对象存储）
  configs/          # 分辨率、跳帧、按 GPU 的 profile（a40 / 1080ti）
```

## 成功标准（可量化）

- [ ] Windows 能导出 YOLO DET/SEG + Depth Anything 的可加载产物（至少 FP16；A40 上尝试 INT8）
- [ ] Linux 上 A40：1080p 管线 DET+SEG+Depth 跑通，有 FPS/显存日志
- [ ] Linux 上 1080 Ti：同一套预处理能跑（允许更小 Depth / 更激进跳帧），有独立 profile
- [ ] 打码与分割坐标与原图对齐（无 letterbox 错位）
- [ ] 能导出可播放的 H.265 MOV
- [ ] 同一段素材能走通 gsplat 离线重建并可视化（优先 A40）
- [ ] 文档写明：各模型权重、输入分辨率、跳帧、两卡各自测得 FPS

## 开放问题

- YOLO26 权重来源与人脸专用 vs 通用 DET 微调
- Depth Anything 变体：A40 可用哪档、1080 Ti 被迫降到哪档
- 运行时引擎统一用 **ONNX Runtime** 还是 **TensorRT**（TRT 引擎不可跨 GPU 架构复用：A40 与 1080 Ti 需分别建 engine）
- 1080 Ti 上的 CUDA/PyTorch/TensorRT 最高可用版本矩阵
- gsplat 依赖的 COLMAP/位姿从何来（SfM vs 假设平面/ORB-SLAM 等）
