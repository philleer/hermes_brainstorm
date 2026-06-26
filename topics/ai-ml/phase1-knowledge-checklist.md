# Phase 1 基础知识清单 — 数值表示与量化原理

> 系统学习量化前的必修基础 | 完成每项后打 ✓

---

## 一、浮点数表示

### 1.1 IEEE 754 格式

| 精度 | 总位数 | Sign | Exponent | Mantissa | Bias | 范围 |
|------|--------|------|----------|----------|------|------|
| FP32 | 32 | 1 | 8 | 23 | 127 | ±3.4×10³⁸ |
| FP16 | 16 | 1 | 5 | 10 | 15 | ±65504 |
| BF16 | 16 | 1 | 8 | 7 | 127 | ±3.4×10³⁸ |

### 1.2 核心公式

```
FP32 值 = (-1)^sign × (1 + mantissa/2^23) × 2^(exponent - 127)

特殊情况:
  exponent = 0,   mantissa = 0   → ±0
  exponent = 0,   mantissa ≠ 0   → subnormal (非规格化数)
  exponent = 255, mantissa = 0   → ±∞
  exponent = 255, mantissa ≠ 0   → NaN
```

### 1.3 关键概念

- [ ] **Machine Epsilon（机器精度）**：使 1.0 + ε ≠ 1.0 的最小 ε
  - FP32: ε ≈ 1.19 × 10⁻⁷
  - FP16: ε ≈ 9.77 × 10⁻⁴

- [ ] **ULP (Unit in the Last Place)**：两个相邻浮点数之间的间距
  - 值越大，ULP 越大（浮点数的"分辨率"不是均匀的）

- [ ] **Subnormal Number（非规格化数）**：比最小规格化数更小的数
  - 牺牲精度换取范围，用来实现 "gradual underflow"

- [ ] **为什么 0.1 + 0.2 ≠ 0.3**：0.1 和 0.2 在二进制中是无限循环小数，存储时已被截断

### 1.4 动手验证

```python
import struct, numpy as np

# 验证 machine epsilon
eps = np.float32(1.0)
while np.float32(1.0) + eps / 2 != np.float32(1.0):
    eps /= 2
assert abs(eps - np.finfo(np.float32).eps) < 1e-10  # ✓

# 验证 0.1 + 0.2 ≠ 0.3
assert np.float32(0.1) + np.float32(0.2) != np.float32(0.3)  # ✓
```

---

## 二、量化基础

### 2.1 对称量化 (Symmetric Quantization)

```
公式:
  scale = max(|x|) / (2^(B-1) - 1)
  q = clip(round(x / scale), -2^(B-1), 2^(B-1) - 1)
  x̂ = q × scale

特点:
  - zero_point = 0（原点映射到 0）
  - 权重分布对称时效果好
  - 实现简单，硬件友好
```

### 2.2 非对称量化 (Asymmetric Quantization)

```
公式:
  scale = (x_max - x_min) / (2^B - 1)
  zero_point = round(-x_min / scale)
  q = clip(round(x / scale) + zero_point, 0, 2^B - 1)
  x̂ = (q - zero_point) × scale

特点:
  - 可以处理非对称分布（如 ReLU 输出全是正数）
  - 多一个 zero_point 参数
  - 精度通常略优于对称量化
```

### 2.3 量化粒度

| 粒度 | scale 数量 | 精度 | 开销 |
|------|-----------|------|------|
| Per-tensor | 1 个（整个 tensor 共享） | 最低 | 最小 |
| Per-channel | N 个（每个 channel 一个） | 较高 | 较小 |
| Per-group | N×M 个（分组共享） | 最高 | 较大 |

**为什么 Per-channel 更好**：

```
conv 权重 shape: [64, 3, 7, 7]
  Channel 0: 权重范围 [-0.05, 0.05]  ← 需要小的 scale
  Channel 63: 权重范围 [-0.5, 0.5]   ← 需要大的 scale
  Per-tensor: 用同一个 scale → Channel 0 被浪费
  Per-channel: 各自用各自的 scale → 精确
```

### 2.4 动手验证

```python
import numpy as np

def symmetric_quantize(x, bits=8):
    max_val = 2**(bits-1) - 1
    scale = np.max(np.abs(x)) / max_val
    q = np.round(x / scale).clip(-max_val, max_val).astype(np.int8)
    return q, scale

def asymmetric_quantize(x, bits=8):
    max_val = 2**bits - 1
    scale = (x.max() - x.min()) / max_val
    zp = np.round(-x.min() / scale)
    q = (np.round(x / scale) + zp).clip(0, max_val).astype(np.uint8)
    return q, scale, zp

def dequantize(q, scale, zp=0):
    return (q.astype(np.float32) - zp) * scale

# 测试
x = np.random.randn(1000) * 0.5
for bits in [2, 4, 8]:
    q, s = symmetric_quantize(x, bits)
    dq = dequantize(q, s)
    mse = np.mean((x - dq)**2)
    print(f"{bits}-bit MSE: {mse:.6f}")
```

---

## 三、量化误差

### 3.1 统计模型

```
假设: 量化误差 e 服从均匀分布 e ~ Uniform(-scale/2, scale/2)

理论方差:
  σ²_noise = scale² / 12

理论 SNR (满量程正弦信号):
  SNR_dB = 6.02 × B + 1.76
  (B = 量化位数)

验证:
  8-bit:  SNR ≈ 6.02×8 + 1.76 = 49.9 dB
  4-bit:  SNR ≈ 6.02×4 + 1.76 = 25.8 dB
  2-bit:  SNR ≈ 6.02×2 + 1.76 = 13.8 dB
```

### 3.2 误差来源

| 来源 | 说明 | 影响 |
|------|------|------|
| 舍入误差 | round() 截断 | 随机噪声，可控 |
| 饱和误差 | clip() 截断超出范围的值 | 信息丢失，严重 |
| 死区误差 | zero_point 附近的小值被量化为 0 | 小信号丢失 |

### 3.3 动手验证

```python
import numpy as np

def verify_snr(x, bits=8):
    q, s = symmetric_quantize(x, bits)
    dq = dequantize(q, s)
    error = x - dq

    signal_power = np.var(x)
    noise_power = np.var(error)
    snr = 10 * np.log10(signal_power / noise_power)
    theoretical = 6.02 * bits + 1.76
    print(f"实测 SNR: {snr:.2f} dB")
    print(f"理论 SNR: {theoretical:.2f} dB")
    print(f"误差: {abs(snr - theoretical):.2f} dB")

# 测试不同分布
verify_snr(np.random.randn(10000) * 0.3, 8)     # 正态分布
verify_snr(np.random.uniform(-1, 1, 10000), 8)   # 均匀分布
```

---

## 四、量化的 Engineering View

### 4.1 什么决定量化精度

```
量化精度 = f(scale 的选择, 数据分布, bit 数)

关键因素:
  1. scale 的选择      ← 最关键的工程决策
  2. 数据分布特征       ← 正态 vs 均匀 vs 长尾
  3. outlier 处理       ← 少数极端值可能拉偏 scale
  4. calibration 数据量  ← 越多越准，但有边际递减
```

### 4.2 Scale 选择策略

| 策略 | 公式 | 适用场景 |
|------|------|---------|
| MinMax | scale = max(\|x\|) / N | 默认，简单 |
| MSE | scale = argmin MSE(x, x̂) | 精度优先 |
| Percentile | 用 99.9% 分位数代替 max | 有 outlier 时 |
| KL Divergence | 最小化量化前后分布的 KL 散度 | TensorRT 默认 |

### 4.3 Calibration 数据量

```
经验法则:
  CNN 图像模型: 100-500 张
  LLM: 128-512 条文本 (如 Pile 或 C4 子集)
  Too few → scale 不准 → 精度差
  Too many → 边际收益递减，浪费时间
```

### 4.4 常见陷阱

| 陷阱 | 现象 | 解决 |
|------|------|------|
| outlier 拉偏 scale | 大部分值被量化到 0 | 用 percentile 或 clip |
| 第一层没量化 | 精度损失最大的来源 | 考虑用 FP16 |
| 校准数据不代表性 | 推理时精度远低于预期 | 用真实业务数据校准 |
| 不同 batch 的 scale 不一致 | 推理结果不稳定 | 校准后固定 scale |

---

## 五、终极检查点

完成 Phase 1 后，应该能口头回答以下问题（每题 3 句话以内）：

### 5.1 自测题

1. **为什么 FP32 能表示 ±3.4×10³⁸ 这么大的数，却只有约 7 位有效数字？**

2. **对称量化和非对称量化的公式？各自适用什么场景？**

3. **为什么 8-bit 量化的理论 SNR 是 6.02×8 + 1.76 ≈ 50 dB？**

4. **量化误差的统计模型是什么？**

5. **scale 和 zero_point 如何计算？scale 的选择如何影响量化精度？**

### 5.2 实操题

- [ ] 能用 numpy 手写对称/非对称量化函数（不看参考资料）
- [ ] 能解析一个 FP32 的二进制表示（sign/exponent/mantissa）
- [ ] 能用 PyTorch 跑通 dynamic quantization
- [ ] 能画出量化误差的分布直方图，验证 SNR 公式
- [ ] 能解释 per-channel 为什么比 per-tensor 好，并给出量化误差数据

---

## 六、参考资源速查

| 资源 | 类型 | 用途 |
|------|------|------|
| Goldberg 1991 — Floating-Point Arithmetic | 论文/长文 | 浮点数圣经 |
| Gholami 2021 — Survey of Quantization (Section 2) | 综述 | 量化基础公式 |
| Krishnamoorthi 2018 — Quantizing Deep CNNs (Section 3) | 论文 | Per-channel 量化 |
| PyTorch Quantization Docs | 官方文档 | 动手实践 |
| Lei Mao's Blog — Neural Network Quantization | 博客 | 数学推导 + 代码 |

---

*完成全部 5 个自测题 + 5 个实操题 → Phase 1 过关，进入 Phase 2。*