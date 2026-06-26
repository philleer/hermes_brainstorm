# RLHF 与混合精度量化 — 学习路径与前置知识

> 2026-06-16 | 来源：Hermes 对话总结

## 概述

本文档总结 RLHF（Reinforcement Learning from Human Feedback）与混合精度量化的交叉学习路径，覆盖前置知识、核心概念、实验步骤和工具链。

---

## 一、RLHF 管线全景

```
预训练模型 (Base Model)
        │
        ▼
┌─────────────────────────────────┐
│ 阶段1: SFT (Supervised Fine-Tuning)     │
│ 输入: {prompt, answer} 标注对            │
│ 输出: Policy Model                      │
│ 工具: train_sft.py                      │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│ 阶段2: Reward Model Training            │
│ 输入: 偏好对 {prompt, chosen, rejected} │
│ 输出: 能打分的 Reward Model              │
│ 工具: train_reward.py                   │
│ Loss: -log(sigmoid(score_chosen - score_rejected)) │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│ 阶段3: PPO 优化                         │
│ Policy 生成回答 → RM 打分 → PPO 更新    │
│ 加 KL penalty 防止偏离太远              │
│ 工具: train_ppo.py                      │
└─────────────────────────────────┘
        │
        ▼
   对齐后的模型
```

**捷径：DPO (Direct Preference Optimization)**

跳过阶段2（RM 训练），直接用偏好对优化模型。数学上等价于 RLHF 但更简单稳定。

```
工具: train_dpo.py
输入: {prompt, chosen, rejected}
```

---

## 二、精度全景图

### 2.1 数值表示

| 精度 | 位数 | 数值范围 | 有效精度 | 典型用途 |
|------|------|---------|---------|---------|
| FP32 | 32 bit | ±3.4×10³⁸ | ~7 位十进制 | 训练黄金标准 |
| FP16 | 16 bit | ±65504 | ~3 位十进制 | 推理加速 |
| BF16 | 16 bit | ±3.4×10³⁸ | ~2 位十进制 | 训练（范围大，不怕梯度溢出） |
| INT8 | 8 bit | -128~127 | 整数 | 推理量化 |
| NF4 | 4 bit | 16 个非均匀值 | 极低 | QLoRA 存储 |

### 2.2 关键区别

- **FP16 vs BF16**：FP16 精度高但范围小，BF16 范围大但精度低。训练时 BF16 更稳（梯度不易下溢），推理时 FP16 精度更好。
- **INT8 量化**：推理专用，需要 calibration 数据统计 min/max。精度损失 1~5% mAP 常见。
- **NF4 (4-bit NormalFloat)**：信息论最优的 4-bit 量化格式，专为 QLoRA 设计。非均匀分桶，对正态分布权重最优。

---

## 三、QLoRA 原理

### 3.1 核心技巧

```
┌─────────────────────────────────────────┐
│  预训练模型 (冻结，4-bit 存储)            │
│  ┌─────┐ ┌─────┐ ┌─────┐               │
│  │ NF4 │→│ NF4 │→│ NF4 │→ ...          │
│  └─────┘ └─────┘ └─────┘               │
│    ↓ 前向时反量化到 BF16                  │
│  ┌─────┐ ┌─────┐ ┌─────┐               │
│  │BF16 │→│BF16 │→│BF16 │→ ...          │
│  └─────┘ └─────┘ └─────┘               │
│         +                                │
│  ┌──────────┐ ┌──────────┐              │
│  │ LoRA A   │→│ LoRA B   │  ← BF16 训练 │
│  │ (r×din)  │ │ (dout×r) │              │
│  └──────────┘ └──────────┘              │
└─────────────────────────────────────────┘
```

| 技巧 | 作用 |
|------|------|
| NF4 存储 | 4-bit 存储权重，省 8× 显存 |
| BF16 计算 | 前向/反向用 BF16，保精度 |
| LoRA | 只训 0.1% 参数（r=8 时），省梯度显存 |
| Double Quantization | 量化常数也量化，再省 0.4 bit/参数 |
| Paged Optimizers | 优化器状态用统一内存，避免 OOM |

### 3.2 LoRA 参数

```
原始权重 W ∈ R^(d×k)
LoRA: W' = W + B·A   其中 A∈R^(r×k), B∈R^(d×r), r≪min(d,k)

r=8 时，可训练参数 ≈ 原始模型的 0.1%
```

| 超参 | 推荐值 | 说明 |
|------|--------|------|
| r | 8 | 秩，越大越强但越慢 |
| alpha | 16 | 缩放因子，实际学习率 ∝ alpha/r |
| dropout | 0.05 | 防止过拟合 |
| target_modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj | 对哪些层加 LoRA |

---

## 四、混合精度训练

### 4.1 FP16 训练的 Loss Scaling

```
FP32 Master Weight (内存中)
    ↓ 拷贝为 FP16
FP16 Forward Pass (计算快)
    ↓ 计算 loss
FP16 Backward Pass (梯度)
    ↓ 梯度缩放 (Loss Scaling)
FP32 Weight Update (更新 master weight)
```

**为什么需要 Loss Scaling**：FP16 最小正数 ≈ 6×10⁻⁸。很多梯度比这个还小，会被截断为 0。解决方法：反向传播前把 loss 乘一个大数（如 1024），算完梯度再除回来。

### 4.2 精度 vs 资源权衡

```
FP32 训练:  ████████████████ 精度最好，显存最大
BF16 训练:  ████████████     精度稍降，显存减半
FP16 训练:  ██████████       精度降更多，需要 Loss Scaling
QLoRA(4bit):████████████     训练精度接近 FP16，存储只有 1/8
INT8 推理:  ████████         推理精度损失，需要 calibration
```

---

## 五、层敏感度分析

### 5.1 四种方法

| 方法 | 原理 | 速度 | 准确度 | 适合场景 |
|------|------|------|--------|---------|
| **Heuristic** (经验法则) | 基于架构位置判断 | 即时 | 中等 | 快速了解，不需要数据 |
| **Gradient** (梯度近似) | 梯度范数 ≈ 敏感度 | 快 (1次反向) | 较好 | 大模型快速筛选 |
| **Perturbation** (逐层扰动) | 量化每一层看 loss 变化 | 慢 (O(n)次前向) | 好 | 小模型，最直观 |
| **HAWQ** (Hessian迹) | Hutchinson 估算 Hessian 迹 | 很慢 | 最好 | 发论文，需要严谨 |

### 5.2 经验法则速查

```
高敏感层 (必须 FP16):
  - 第一层 conv/embedding
  - 最后一层 / 检测头 / 分类头
  - Attention 中的 QKV 投影
  - LayerNorm / BatchNorm
  - 残差连接的 shortcut/proj

低敏感层 (可以 INT4):
  - 中间层普通 conv
  - FFN 中间层 (gate_proj, up_proj, fc1)
  - 深层 (>70% 位置)

为什么:
  - 第一层: 量化误差被后面所有层放大
  - 最后一层: 量化误差直接反映在输出上
  - 深层: 权重分布集中，量化相对误差小
```

### 5.3 使用工具

```bash
cd D:\misc_codes\agent_playground\llm_practice

# 经验法则 (最快)
python tools/sensitivity_analysis.py --method heuristic --model Qwen/Qwen2-0.5B

# 梯度近似
python tools/sensitivity_analysis.py --method gradient --model Qwen/Qwen2-0.5B

# 逐层扰动
python tools/sensitivity_analysis.py --method perturbation --model Qwen/Qwen2-0.5B

# HAWQ
python tools/sensitivity_analysis.py --method hawq --model Qwen/Qwen2-0.5B

# 输出 JSON 报告
python tools/sensitivity_analysis.py --method heuristic --model Qwen/Qwen2-0.5B --output report.json
```

---

## 六、实验路线图

### 6.1 前置知识学习顺序

| 序号 | 知识点 | 时间 | 资料 |
|------|--------|------|------|
| 1 | FP16/BF16/FP32 的 IEEE 754 表示 | 2h | 维基百科 |
| 2 | QLoRA 论文精读 | 4h | Dettmers et al. 2023 |
| 3 | bitsandbytes 库的基本用法 | 2h | 官方文档 |
| 4 | PEFT/LoRA 原理 | 2h | Hu et al. 2021 |
| 5 | PPO 算法基础 | 4h | Schulman et al. 2017 |
| 6 | 混合精度训练的 Loss Scaling | 1h | NVIDIA 文档 |

### 6.2 实验步骤

```
Step 1: 跑通 SFT (QLoRA)
  └─ python sft/train_sft.py --model_name Qwen/Qwen2-0.5B --use_qlora
     预期: 确认环境可用，理解 QLoRA 的存储/计算分离

Step 2: 对比 SFT 前后
  └─ 同 prompt 输入，对比原始模型和 SFT 后模型的输出
     预期: 直观感受微调效果

Step 3: 跑通 DPO
  └─ python dpo/train_dpo.py --model_name ./output/sft_model
     预期: 理解偏好对齐，跳过 RM 训练

Step 4: 构造偏好数据
  └─ 理解 {prompt, chosen, rejected} 格式
     预期: 掌握数据准备能力

Step 5: 研究 QLoRA 超参
  └─ 对比 r=4/8/16, alpha=8/16/32 的 loss 曲线
     预期: 理解量化精度 vs 训练效果

Step 6: 完整 RLHF 管线
  └─ SFT → RM → PPO 全流程
     预期: 端到端理解 RLHF
```

### 6.3 环境约束

- 此机器: Windows 10, PyTorch 2.5.1+cpu, 无 GPU
- 推荐模型: Qwen2-0.5B (CPU 可承受)
- QLoRA 在 CPU 上能跑但较慢，完整 PPO 管线可能太慢
- 建议优先跑通 SFT 和 DPO，PPO 留到有 GPU 时

---

## 七、关键概念速查

| 术语 | 一句话解释 |
|------|-----------|
| SFT | 用标注数据直接监督微调 |
| RM | 训练一个模型给回答打分 |
| PPO | 用 RM 的信号做策略梯度优化 |
| DPO | 跳过 RM，直接用偏好对优化 |
| QLoRA | 4-bit 存储 + LoRA 微调，省 8× 显存 |
| Loss Scaling | FP16 训练时放大 loss 防止梯度下溢 |
| Calibration | 收集数据统计 min/max 用于量化 |
| Per-channel Quant | 逐通道量化，比逐层量化更准 |
| KL Penalty | PPO 中防止模型偏离太远的约束项 |
| Bradley-Terry | RM 训练用的 Loss: -log(σ(score_chosen - score_rejected)) |

---

## 八、相关文件

```
D:\misc_codes\agent_playground\llm_practice\
├── sft/train_sft.py              ← SFT 训练 (QLoRA/Full)
├── dpo/train_dpo.py              ← DPO 训练
├── rlhf/train_reward.py          ← Reward Model 训练
├── rlhf/train_ppo.py             ← PPO 训练
├── tools/sensitivity_analysis.py ← 层敏感度分析
├── data/                         ← 样本数据
└── configs/                      ← 配置文件
```

---

*本文档由 Hermes Agent 对话总结生成，可作为后续学习的参考基线。*