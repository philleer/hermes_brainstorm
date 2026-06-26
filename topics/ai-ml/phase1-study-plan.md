# Phase 1 学习计划 — 数值基础与量化原理

> 每天 1-1.5 小时 | 共 12 天 | 2026.06

---

## 第一周：从浮点数到量化公式

### Day 1（周一）— 浮点数的二进制表示

| 时间 | 内容 |
|------|------|
| 20min | 读 Goldberg 第 1 章 "Rounding Error"（开头到 "Relative Error and Ulps"） |
| 20min | 理解 FP32 的 1-8-23 结构：1 bit sign + 8 bit exponent + 23 bit mantissa |
| 20min | 动手：用 Python 解析一个浮点数的二进制表示 |

**动手题**：

```python
import struct

def float_to_binary(f):
    """把 FP32 浮点数分解为 sign/exponent/mantissa"""
    bits = struct.pack('>f', f)  # 大端序
    # 你的代码：解析这 4 个字节
    # 提示：int.from_bytes(bits, 'big') 得到 32 位整数
    pass

# 测试
float_to_binary(3.14)
float_to_binary(0.1)   # 为什么 0.1 不能精确表示？
float_to_binary(1e38)  # 最大能表示多少？
```

**今日产出**：一份 Python 脚本，能输入任意浮点数，输出其 sign/exponent/mantissa 和十进制近似值。

---

### Day 2（周二）— 浮点数的精度与范围

| 时间 | 内容 |
|------|------|
| 25min | 读完 Goldberg 第 2 章前半（"IEEE 754 格式"） |
| 20min | 理解三个关键概念：machine epsilon、ulp、subnormal numbers |
| 20min | 动手：计算 FP32 和 FP16 的理论精度和范围 |

**动手题**：

```python
import numpy as np

# 1. 验证 machine epsilon
eps = np.float32(1.0)
while np.float32(1.0) + eps / np.float32(2.0) != np.float32(1.0):
    eps /= np.float32(2.0)
print(f"FP32 epsilon: {eps}")  # 应该 ≈ 1.19e-7

# 2. 验证 0.1 + 0.2 ≠ 0.3
a = np.float32(0.1)
b = np.float32(0.2)
c = np.float32(0.3)
print(f"0.1 + 0.2 = {a + b}")       # 0.30000001192092896
print(f"0.1 + 0.2 == 0.3: {a + b == c}")  # False

# 3. 找出 FP32 能表示的最小正数
print(f"FP32 min normal: {np.float32(np.finfo(np.float32).tiny)}")
```

**今日产出**：理解为什么 FP32 有 ~7 位有效数字、范围 ±3.4×10³⁸。

---

### Day 3（周三）— 量化公式推导

| 时间 | 内容 |
|------|------|
| 15min | 读 Gholami Section 2.1 "Quantization Basics" |
| 15min | 推导对称量化和非对称量化公式 |
| 30min | 动手：numpy 实现完整的 quantizer + dequantizer |

**动手题**：

```python
import numpy as np

def symmetric_quantize(x, bits=8):
    """对称量化: q = round(x / scale), 范围 [-2^(bits-1), 2^(bits-1)-1]"""
    max_val = 2**(bits-1) - 1
    scale = np.max(np.abs(x)) / max_val
    x_q = np.round(x / scale).clip(-max_val, max_val)
    return x_q.astype(np.int8), scale

def asymmetric_quantize(x, bits=8):
    """非对称量化: q = round(x / scale) + zero_point, 范围 [0, 2^bits-1]"""
    max_val = 2**bits - 1
    x_min, x_max = np.min(x), np.max(x)
    scale = (x_max - x_min) / max_val
    zero_point = np.round(-x_min / scale)
    x_q = (np.round(x / scale) + zero_point).clip(0, max_val)
    return x_q.astype(np.uint8), scale, zero_point

def dequantize(x_q, scale, zero_point=0):
    """反量化: x = (q - zero_point) * scale"""
    return (x_q.astype(np.float32) - zero_point) * scale

# 测试
x = np.random.randn(1000) * 0.5
for bits in [2, 4, 8]:
    x_q, scale = symmetric_quantize(x, bits)
    x_dq = dequantize(x_q, scale)
    mse = np.mean((x - x_dq)**2)
    print(f"{bits}-bit MSE: {mse:.6f}")
```

**今日产出**：一个 `quantize.py` 工具模块，包含对称/非对称量化函数。

---

### Day 4（周四）— 量化误差分析

| 时间 | 内容 |
|------|------|
| 15min | 读 Krishnamoorthi Section 3.1-3.2 |
| 15min | 理解量化噪声的统计模型（均匀分布假设） |
| 30min | 动手：量化误差的统计分析和可视化 |

**动手题**：

```python
import numpy as np
import matplotlib.pyplot as plt

def analyze_quantization_error(x, bits=8):
    x_q, scale = symmetric_quantize(x, bits)
    x_dq = dequantize(x_q, scale)
    error = x - x_dq

    # 1. 误差分布
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 3, 1)
    plt.hist(x, bins=50, alpha=0.5, label='原始')
    plt.hist(x_dq, bins=50, alpha=0.5, label=f'{bits}-bit')
    plt.legend()

    plt.subplot(1, 3, 2)
    plt.hist(error, bins=50)
    plt.title(f'量化误差分布 (MSE={np.mean(error**2):.6f})')

    plt.subplot(1, 3, 3)
    plt.scatter(x, error, alpha=0.3, s=1)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('原始值')
    plt.ylabel('量化误差')

    # 2. 验证 SNR 公式: SNR ≈ 6.02B + 1.76 dB
    signal_power = np.var(x)
    noise_power = np.var(error)
    snr = 10 * np.log10(signal_power / noise_power)
    theoretical = 6.02 * bits + 1.76
    print(f"实测 SNR: {snr:.2f} dB, 理论 SNR: {theoretical:.2f} dB")

# 测试不同分布的数据
x_uniform = np.random.uniform(-1, 1, 10000)
x_normal = np.random.randn(10000) * 0.3
analyze_quantization_error(x_normal, 8)
```

**今日产出**：一份量化误差分析报告，验证 SNR 公式，理解误差分布。

---

### Day 5（周五）— Per-tensor vs Per-channel 量化

| 时间 | 内容 |
|------|------|
| 15min | 读 Krishnamoorthi Section 3.3 "Per-channel quantization" |
| 15min | 理解为什么 conv 权重适合逐通道量化 |
| 30min | 动手：对比两种量化方式在真实权重上的精度差异 |

**动手题**：

```python
import torch
import torchvision.models as models

# 加载一个预训练模型，提取一层 conv 权重
model = models.resnet18(pretrained=True)
conv_weight = model.conv1.weight.data  # shape: [64, 3, 7, 7]

# 1. Per-tensor: 整个 tensor 用同一个 scale
w_flat = conv_weight.flatten()
scale_tensor = torch.max(torch.abs(w_flat)) / 127
w_q_tensor = torch.round(w_flat / scale_tensor).clip(-128, 127)
w_dq_tensor = w_q_tensor * scale_tensor
mse_tensor = torch.mean((w_flat - w_dq_tensor)**2)

# 2. Per-channel: 每个 output channel 有自己的 scale
w_dq_channel = torch.empty_like(conv_weight)
for c in range(conv_weight.shape[0]):
    w_c = conv_weight[c].flatten()
    scale_c = torch.max(torch.abs(w_c)) / 127
    w_q_c = torch.round(w_c / scale_c).clip(-128, 127)
    w_dq_channel[c] = (w_q_c * scale_c).reshape(conv_weight.shape[1:])
mse_channel = torch.mean((conv_weight - w_dq_channel)**2)

print(f"Per-tensor  MSE: {mse_tensor:.6f}")
print(f"Per-channel MSE: {mse_channel:.6f}")
print(f"改善: {(1 - mse_channel/mse_tensor)*100:.1f}%")

# 3. 可视化各 channel 的权重分布
import matplotlib.pyplot as plt
fig, axes = plt.subplots(2, 4, figsize=(12, 6))
for i in range(8):
    ax = axes[i//4, i%4]
    ax.hist(conv_weight[i].flatten().numpy(), bins=50)
    ax.set_title(f'Channel {i}')
plt.tight_layout()
```

**今日产出**：理解为什么 per-channel 量化几乎总是优于 per-tensor，以及什么时候用哪种。

---

### Day 6（周六）— 复习 + 公式 Cheat Sheet

| 时间 | 内容 |
|------|------|
| 30min | 整理 Week 1 所有公式，手写一份 Cheat Sheet |
| 30min | 重做 Day 3 的量化函数，不看参考 |
| 20min | 用白纸默写 IEEE 754 的 1-8-23 结构图 |

**Cheat Sheet 应包含**：

```
对称量化:  q = clip(round(x / s), -N, N-1)    where s = max(|x|) / N
非对称量化: q = clip(round(x / s) + z, 0, 2^B-1) where s = (x_max - x_min)/(2^B-1)
                                                      z = round(-x_min / s)
反量化:    x̂ = (q - z) * s  (非对称) 或 x̂ = q * s (对称)

SNR 公式:  SNR_dB ≈ 6.02B + 1.76  (B = bits)
量化噪声:  noise ~ Uniform(-s/2, s/2), 方差 = s²/12

FP32 结构: 1 | 8 | 23  (sign | exponent | mantissa)
FP16 结构: 1 | 5 | 10
BF16 结构: 1 | 8 | 7
```

---

## 第二周：从理论到实践

### Day 7（周日）— PyTorch 量化基础

| 时间 | 内容 |
|------|------|
| 15min | 读 PyTorch 官方文档 "Introduction to Quantization" |
| 15min | 理解三种量化模式：dynamic / static / QAT |
| 30min | 动手：PyTorch 的 dynamic quantization |

**动手题**：

```python
import torch
import torch.quantization as quant
from torchvision.models import resnet18

# Dynamic Quantization — 最简单的量化
model = resnet18(pretrained=True)
model.eval()

# 只量化 Linear 和 LSTM 层（权重 INT8，激活值运行时量化）
model_int8 = quant.quantize_dynamic(
    model,
    {torch.nn.Linear},  # 量化哪些层
    dtype=torch.qint8,
)

# 对比模型大小
torch.save(model.state_dict(), 'model_fp32.pt')
torch.save(model_int8.state_dict(), 'model_int8.pt')
print(f"FP32: {os.path.getsize('model_fp32.pt')/1e6:.1f} MB")
print(f"INT8: {os.path.getsize('model_int8.pt')/1e6:.1f} MB")
```

**今日产出**：理解 PyTorch 的三种量化模式，跑通 dynamic quantization。

---

### Day 8（周一）— PTQ 完整流程

| 时间 | 内容 |
|------|------|
| 20min | 读 PyTorch 官方 "Static Quantization with Eager Mode" 教程 |
| 30min | 动手：完整的 PTQ 流程（calibration → 量化 → 推理） |
| 10min | 对比量化前后的精度和速度 |

**动手题**：

```python
import torch
import torch.quantization as quant
from torchvision.models import resnet18

# 1. 准备模型
model = resnet18(pretrained=True)
model.eval()

# 2. 设置 qconfig（选择量化策略）
model.qconfig = quant.get_default_qconfig('fbgemm')
# 备选: quant.get_default_qconfig('qnnpack')  # ARM CPU

# 3. 插入观察者（FakeQuantize）
model_prepared = quant.prepare(model)

# 4. Calibration — 用少量数据统计激活值范围
calibration_data = torch.randn(100, 3, 224, 224)
for i in range(0, 100, 10):
    model_prepared(calibration_data[i:i+10])

# 5. 转换为 INT8 模型
model_int8 = quant.convert(model_prepared)

# 6. 对比
input_tensor = torch.randn(1, 3, 224, 224)
with torch.no_grad():
    out_fp32 = model(input_tensor)
    out_int8 = model_int8(input_tensor)

diff = (out_fp32 - out_int8).abs().mean()
print(f"FP32 vs INT8 输出差异: {diff:.6f}")
```

**今日产出**：完整的 PTQ pipeline，理解 calibration 的作用。

---

### Day 9（周二）— FakeQuantize 深入

| 时间 | 内容 |
|------|------|
| 20min | 读 PyTorch `FakeQuantize` 源码 |
| 25min | 动手：自己实现一个 FakeQuantize 模块 |
| 15min | 理解 Observer 的工作机制（MinMaxObserver, MovingAverageMinMaxObserver） |

**动手题**：

```python
import torch
import torch.nn as nn

class MyFakeQuantize(nn.Module):
    """自己实现 FakeQuantize: 前向模拟量化，反向直通"""
    def __init__(self, bits=8, symmetric=True):
        super().__init__()
        self.bits = bits
        self.symmetric = symmetric
        self.register_buffer('scale', torch.tensor(1.0))
        self.register_buffer('zero_point', torch.tensor(0))

    def forward(self, x):
        if self.training:
            # 训练时: 更新 scale/zero_point
            if self.symmetric:
                self.scale = x.abs().max() / (2**(self.bits-1) - 1)
            else:
                self.scale = (x.max() - x.min()) / (2**self.bits - 1)
                self.zero_point = (-x.min() / self.scale).round()

        # 量化 → 反量化（模拟量化误差）
        x_q = (x / self.scale + self.zero_point).round()
        x_q = x_q.clamp(0 if not self.symmetric else -2**(self.bits-1),
                         2**self.bits - 1 if not self.symmetric else 2**(self.bits-1)-1)
        x_dq = (x_q - self.zero_point) * self.scale

        # 关键: Straight-Through Estimator (STE)
        # 前向用带误差的 x_dq，反向梯度直接传回 x
        return x_dq.detach() + x - x.detach()

# 测试: 把它插入一个简单网络
class TinyNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 16, 3)
        self.quant = MyFakeQuantize(bits=8)
        self.fc = nn.Linear(16 * 30 * 30, 10)

    def forward(self, x):
        x = self.conv(x)
        x = self.quant(x)  # 在这里插入量化
        x = x.view(x.size(0), -1)
        return self.fc(x)
```

**今日产出**：理解 FakeQuantize 的 STE（Straight-Through Estimator）机制，能自己实现量化模块。

---

### Day 10（周三）— 量化敏感度可视化

| 时间 | 内容 |
|------|------|
| 15min | 复习 Day 5 的 per-channel 分析，扩展到逐层分析 |
| 30min | 动手：用工具脚本分析 ResNet-18 的层敏感度 |
| 15min | 画出敏感度热力图，标记高敏感层 |

**动手题**：

```bash
cd D:\misc_codes\agent_playground\llm_practice
python tools/sensitivity_analysis.py \
    --method heuristic \
    --model Qwen/Qwen2-0.5B \
    --output sensitivity_report.json
```

然后手写一份分析笔记，回答：
- 前 10% 最敏感的层是哪些？为什么？
- 后 10% 最不敏感的层是哪些？为什么？
- 如果只给 15% 的层用 FP16，你会选哪些？

**今日产出**：一份敏感度分析报告 + 手动标注的精度分配方案。

---

### Day 11（周四）— 综合实验

| 时间 | 内容 |
|------|------|
| 45min | 从头到尾跑一遍完整的量化实验 |
| 15min | 写实验报告 |

**实验任务**：

```
1. 加载 ResNet-18 或 Qwen2-0.5B
2. 做敏感度分析，标记高/中/低敏感层
3. 对高敏感层用 FP16，中敏感用 INT8，低敏感用 INT4
4. 对比：
   - 全 FP32 的精度
   - 全 INT8 的精度
   - 混合精度的精度
5. 回答：混合精度相比全 INT8 提升了多少？代价是什么？
```

**今日产出**：一份完整的混合精度量化实验报告。

---

### Day 12（周五）— 总结 + Phase 2 衔接

| 时间 | 内容 |
|------|------|
| 30min | 整理 Phase 1 全部笔记，补充缺失 |
| 30min | 完成 Phase 1 检查点的 5 个问题（口头回答或写下来） |

**最终检查点**：

1. 为什么 FP32 能表示 3.4×10³⁸ 却只有约 7 位有效数字？
2. 对称量化和非对称量化的公式？什么时候用哪个？
3. 为什么 8-bit 量化的 SNR ≈ 50 dB？
4. 量化误差的统计模型是什么？
5. scale 和 zero_point 如何计算？scale 的选择如何影响精度？

全部能回答 → Phase 1 过关，进入 Phase 2（CNN 量化 PTQ/QAT）。

---

## 打卡表

```
Week 1
□ Day 1 (周一) — 浮点数二进制表示         [ ]
□ Day 2 (周二) — 浮点数精度与范围         [ ]
□ Day 3 (周三) — 量化公式推导             [ ]
□ Day 4 (周四) — 量化误差分析             [ ]
□ Day 5 (周五) — Per-tensor vs Per-channel [ ]
□ Day 6 (周六) — 复习 + Cheat Sheet       [ ]

Week 2
□ Day 7 (周日) — PyTorch 量化基础         [ ]
□ Day 8 (周一) — PTQ 完整流程             [ ]
□ Day 9 (周二) — FakeQuantize 深入        [ ]
□ Day 10(周三) — 敏感度可视化             [ ]
□ Day 11(周四) — 综合实验                 [ ]
□ Day 12(周五) — 总结 + Phase 2 衔接      [ ]
```

---

*每个 Day 的动手题都可以在 `D:\misc_codes\agent_playground\llm_practice\phase1_exercises\` 下创建对应的 `.py` 文件。*