# 模型量化与部署 — 系统学习路线

> 覆盖 CNN 和 Transformer 两大架构的量化理论、工具链与部署实践

---

## 学习路线总览

```
Phase 1: 数值基础        (1 周)  数的表示、量化误差
Phase 2: CNN 量化        (2 周)  PTQ、QAT、per-channel
Phase 3: Transformer 量化 (2 周)  Attention 量化、KV Cache、LLM 部署
Phase 4: 部署实践        (2 周)  工具链、板端推理、Benchmark
Phase 5: 进阶            (持续)  混合精度、硬件感知、NAS+量化
```

---

## Phase 1: 数值基础（1 周）

### 目标
理解计算机如何表示数字，量化误差从哪来，为什么 8 个 bit 能近似 32 个 bit 的信息。

### 必学

| 主题 | 核心问题 | 资料 |
|------|---------|------|
| IEEE 754 浮点数 | FP32 的 1-8-23 结构是什么？ | 维基百科 "IEEE 754" |
| 定点数 vs 浮点数 | INT8 和 FP32 的本质区别 | 任何数字电路教材第 1 章 |
| 量化公式 | scale 和 zero_point 怎么算？ | `q = round(x/scale) + zero_point` |
| 量化误差 | 为什么量化后精度会掉？ | 信号处理中的量化噪声 |

### 动手

```python
import numpy as np

# 1. 手动实现对称量化
x = np.random.randn(1000) * 0.5
scale = np.max(np.abs(x)) / 127
x_q = np.round(x / scale).clip(-128, 127)
x_dq = x_q * scale
error = np.mean((x - x_dq) ** 2)
print(f"MSE: {error:.6f}")

# 2. 对比不同 bit 的量化误差
for bits in [2, 4, 8, 16]:
    levels = 2 ** bits
    scale = np.max(np.abs(x)) / (levels // 2 - 1)
    x_q = np.round(x / scale).clip(-levels//2, levels//2-1)
    x_dq = x_q * scale
    print(f"{bits}-bit MSE: {np.mean((x - x_dq)**2):.6f}")

# 3. 可视化：看量化前后的分布变化
import matplotlib.pyplot as plt
plt.hist(x, bins=50, alpha=0.5, label='FP32')
plt.hist(x_dq, bins=50, alpha=0.5, label=f'{bits}-bit')
plt.legend()
```

### 检查点
- [ ] 能手写出对称量化/非对称量化的公式
- [ ] 能解释为什么 B-bit 量化的理论 SNR ≈ 6.02B + 1.76 dB
- [ ] 能用 numpy 实现一个 toy quantizer

---

## Phase 2: CNN 量化（2 周）

### 目标
理解 CNN 量化的标准流程，能对 YOLO/ResNet 做 PTQ 和 QAT。

### 第 1 周：后训练量化 (PTQ)

| 主题 | 核心问题 | 参考 |
|------|---------|------|
| PTQ 流程 | calibration → 统计 min/max → 量化 | PyTorch 官方 Quantization 教程 |
| Calibration | 需要多少张图？什么分布最好？ | 论文: "A Survey of Quantization Methods" (Gholami 2021) |
| Per-tensor vs Per-channel | 为什么逐通道更好？ | conv 权重的 channel-wise 分布差异 |
| 激活值量化 | 激活值的范围怎么确定？ | 动态范围 vs 运行时统计 |
| 量化误差传播 | 为什么第一层和最后一层最敏感？ | 误差逐层放大的直觉 + 数学 |

**动手**：

```python
import torch
import torch.quantization as quant

# PyTorch 原生 PTQ
model = torchvision.models.resnet18(pretrained=True)
model.eval()

# 1. 设置量化配置
model.qconfig = quant.get_default_qconfig('fbgemm')
# 2. 插入观察者
model_prepared = quant.prepare(model)
# 3. Calibration (用 100 张图跑一遍)
for images in calibration_loader:
    model_prepared(images)
# 4. 转换
model_int8 = quant.convert(model_prepared)
```

### 第 2 周：量化感知训练 (QAT)

| 主题 | 核心问题 | 参考 |
|------|---------|------|
| QAT 原理 | 为什么训练时模拟量化能恢复精度？ | 论文: "Quantization and Training" (Jacob 2018) |
| Fake Quantization | 前向用 int8 模拟，反向用 float 更新 | PyTorch `FakeQuantize` |
| QAT 训练策略 | 从头训 vs 微调？学习率怎么设？ | 通常从预训练开始，lr 降低 10× |
| QAT vs PTQ 精度对比 | 什么时候 QAT 值得做？ | PTQ 掉 >3% 精度时上 QAT |

**动手**：

```python
# QAT 的关键区别：训练时插入 FakeQuantize
model.train()
model.qconfig = quant.get_default_qat_qconfig('fbgemm')
model_prepared = quant.prepare_qat(model)

# 正常训练循环
for epoch in range(5):
    for images, labels in train_loader:
        output = model_prepared(images)
        loss = criterion(output, labels)
        loss.backward()
        optimizer.step()

# 训练完成后转换
model_int8 = quant.convert(model_prepared)
```

### 检查点
- [ ] 能手动画出 PTQ 的 calibration → 量化流程
- [ ] 能解释 per-channel 为什么比 per-tensor 好
- [ ] 能跑通一个 ResNet/MobileNet 的 INT8 量化
- [ ] 能量化前后精度差异 < 2%

---

## Phase 3: Transformer 量化（2 周）

### 目标
理解 Transformer 特有的量化难点，能对 LLM/ViT 做量化。

### 为什么 Transformer 比 CNN 难量化

```
CNN:                            Transformer:
┌──────────┐                    ┌──────────┐
│  Conv    │  ← 权重分布平稳     │  Attention│  ← 激活值有极端 outlier
│  BN      │  ← 归一化           │  LayerNorm│  ← 归一化后分布变化大
│  ReLU    │  ← 简单激活         │  GELU    │  ← 非线性，范围难预测
│  Pool    │                     │  Softmax │  ← 输入范围极度敏感
└──────────┘                    │  KV Cache│  ← 需要单独处理
                                 └──────────┘
```

### 第 1 周：Attention 量化

| 主题 | 核心问题 | 参考 |
|------|---------|------|
| Activation outlier | 为什么某些 channel 的值特别大？ | 论文: "LLM.int8()" (Dettmers 2022) |
| Per-channel 的局限 | 为什么逐通道量化 Attention 不够？ | token 维度的 outlier |
| LLM.int8() 混合精度 | outliers 用 FP16，其余用 INT8 | 论文 + bitsandbytes 源码 |
| SmoothQuant | 把激活值的量化难度转移给权重 | 论文: "SmoothQuant" (Xiao 2023) |
| KV Cache 量化 | 怎么量化 Key/Value cache？ | 论文: "KVQuant", "KIVI" |

**LLM.int8() 核心思想**：

```
输入矩阵 X ∈ R^(seq_len × hidden_dim)

逐列扫描 → 找出 outlier columns (值 > 阈值的列)
    │
    ├── outlier columns  → 保持 FP16 → 精确计算
    └── 正常 columns     → 量化到 INT8 → 快速计算
    │
    └── 结果合并
```

### 第 2 周：LLM 量化

| 主题 | 核心问题 | 参考 |
|------|---------|------|
| GPTQ | 逐层量化 + 权重补偿 | 论文: "GPTQ" (Frantar 2023) |
| AWQ | 只保护 1% 的 salient weights | 论文: "AWQ" (Lin 2024) |
| GGUF/GGML | llama.cpp 的量化格式 | llama.cpp 源码 |
| QLoRA 再审视 | 4-bit 训练为什么能工作 | 论文: "QLoRA" (Dettmers 2023) |
| 量化后推理 | vLLM, llama.cpp 的 KV cache 管理 | 官方文档 |

**动手**：

```python
# 用 bitsandbytes 加载 4-bit 模型
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2-0.5B",
    quantization_config=bnb_config,
    device_map="auto",
)
print(f"模型大小: {model.get_memory_footprint() / 1e9:.2f} GB")
```

### 检查点
- [ ] 能解释为什么 Transformer 的激活值量化比 CNN 难
- [ ] 理解 LLM.int8() 的混合精度策略
- [ ] 能用 bitsandbytes 加载 4-bit/8-bit 模型
- [ ] 了解 GPTQ、AWQ、SmoothQuant 的核心区别

---

## Phase 4: 部署实践（2 周）

### 目标
把量化后的模型真正跑在目标硬件上，会 Benchmark，会排查问题。

### 第 1 周：工具链

| 平台 | 工具链 | 输入格式 | 量化方式 |
|------|--------|---------|---------|
| NVIDIA GPU | TensorRT | ONNX | INT8/FP16 |
| Horizon X5 BPU | hb_mapper | ONNX → .bin | INT8/INT16 |
| Rockchip NPU | rknn-toolkit | ONNX → .rknn | INT8/FP16 |
| Mobile CPU | TFLite / ONNX Runtime | .tflite / .onnx | INT8 |
| Apple ANE | coremltools | .mlmodel | FP16/INT8 |

### 第 2 周：端到端 Benchmark

| 指标 | 测量方法 | 为什么重要 |
|------|---------|-----------|
| 推理延迟 (p50/p95/p99) | 1000 次推理取分位数 | 99 分位延迟决定用户体验 |
| 吞吐量 | 每秒处理帧数 | 实时系统需要满足帧率要求 |
| 模型大小 | .bin / .rknn 文件大小 | 存储和加载时间 |
| 内存占用 | 运行时 DDR / SRAM | 板端内存通常很紧张 |
| 精度损失 | mAP / mIoU / Perplexity | 量化是否过度牺牲精度 |
| 功耗 | 板端功率计 | 电池供电场景 |

**Benchmark 模板**：

```python
import time
import numpy as np

def benchmark(model, inputs, warmup=50, runs=1000):
    """统一 Benchmark 函数"""
    # 预热
    for _ in range(warmup):
        model(inputs)

    # 计时
    latencies = []
    for _ in range(runs):
        start = time.perf_counter()
        model(inputs)
        latencies.append((time.perf_counter() - start) * 1000)  # ms

    latencies = np.array(latencies)
    return {
        "p50": np.percentile(latencies, 50),
        "p95": np.percentile(latencies, 95),
        "p99": np.percentile(latencies, 99),
        "mean": np.mean(latencies),
        "std": np.std(latencies),
    }
```

### 检查点
- [ ] 能用一种工具链完成 ONNX → 芯片格式的转换
- [ ] 能跑通端到端 Benchmark 并输出延迟分位数
- [ ] 能定位 unsupported op 并给出替代方案
- [ ] 能写出完整的模型部署文档

---

## Phase 5: 进阶（持续）

### 主题

| 主题 | 核心问题 | 参考 |
|------|---------|------|
| 混合精度量化 | 逐层分配精度最优解 | HAWQ, HAWQ-V2, ZeroQ |
| 硬件感知量化 | 怎么把延迟纳入搜索目标？ | 论文: "HAQ" (Wang 2019) |
| 量化 + NAS | 同时搜索架构和精度 | 论文: "APQ" (Wang 2021) |
| 训练后量化微调 | PTQ 后少量数据微调 | AdaRound, BRECQ |
| 二值/三值网络 | 1-bit 权重的极限 | XNOR-Net, Bi-Real Net |
| 量化 + 稀疏化 | INT4 + 50% 稀疏 = 极致的压缩 | SparseGPT, Wanda |

---

## 学习资源清单

### 论文（按推荐阅读顺序）

| 序号 | 论文 | 关键词 | 难度 |
|------|------|--------|------|
| 1 | Jacob et al. 2018 — "Quantization and Training" | INT8 QAT 开山之作 | ★★ |
| 2 | Krishnamoorthi 2018 — "Quantizing deep convolutional networks" | Per-channel 量化 | ★★ |
| 3 | Nagel et al. 2021 — "A White Paper on Neural Network Quantization" | 综述，必读 | ★★ |
| 4 | Dettmers et al. 2022 — "LLM.int8()" | Transformer 混合精度 | ★★★ |
| 5 | Xiao et al. 2023 — "SmoothQuant" | 转移量化难度 | ★★★ |
| 6 | Frantar et al. 2023 — "GPTQ" | 逐层量化+补偿 | ★★★★ |
| 7 | Lin et al. 2024 — "AWQ" | 只保护 1% 权重 | ★★★ |
| 8 | Dettmers et al. 2023 — "QLoRA" | 4-bit 训练 | ★★★ |
| 9 | Gholami et al. 2021 — "A Survey of Quantization Methods" | 长篇综述 | ★★★ |

### 代码库

| 项目 | 用途 |
|------|------|
| PyTorch Quantization | 官方 PTQ/QAT 教程 |
| bitsandbytes | LLM.int8(), NF4 量化 |
| AutoGPTQ | GPTQ 量化 |
| llama.cpp | GGUF 量化 + CPU 推理 |
| TensorRT | NVIDIA GPU 部署 |
| ONNX Runtime | 跨平台推理 |

### 实验建议

```
Phase 1: numpy 手写 quantizer
Phase 2: PyTorch PTQ/QAT 跑 ResNet-18
Phase 3: bitsandbytes 加载 Qwen2-0.5B 4-bit
Phase 4: hb_mapper 转换 YOLO → X5 BPU
Phase 5: 读论文 + 复现
```

---

## 与你的现有工作的对接

```
你已有的:                         学习路线中的位置:
─────────────────────────────────────────────────
X5 BPU 模型转换 (hb_mapper)    →  Phase 4 部署实践 ✓
YOLO 检测/分割部署              →  Phase 2 CNN 量化
混合精度量化的需求              →  Phase 5 进阶
LLM 微调实验 (SFT/DPO/RLHF)    →  Phase 3 Transformer 量化
敏感度分析工具                   →  Phase 2/5 桥梁
```

**建议的切入顺序**：你的 CNN 量化（Phase 2）有实践经验但理论可能碎片化，建议先系统补 Phase 1-2，然后 Phase 3 的 Transformer 量化对你来说是新领域但跟 LLM 微调兴趣直接相关，最后 Phase 4 你已经会了可以快速过。

---

*本文档可作为系统学习量化的路线图，每个 Phase 的检查点用来确认是否真正掌握。*