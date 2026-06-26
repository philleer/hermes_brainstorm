# C++ 设计模式学习路径

> 核心理念：**逆向工程法** — 不要死记硬背模式定义，而是从优秀开源项目中反向识别"为什么这里用了这个模式"。
>
> 小项目 > 大项目。代码量少才能快速看清全局结构。
>
> 如果把 Autoware 和 Apollo 比作用砖瓦盖起的现代化高楼，那么 Folly、Poco 和 LLVM 就是**烧制这些高砖、提供地基钢筋的核心技术**。

---

## 一、推荐深度挖掘的项目

### 应用层：自动驾驶系统架构

#### 1. Autoware (ROS 2 / Universe) — SOA 与现代 C++ 教科书

Autoware Universe 大量使用 C++17/20，是学习面向服务架构（SOA）在实时系统中落地的绝佳素材。

| 核心机制 | 对应设计模式 | 为什么值得看 |
|----------|-------------|-------------|
| **Component 组件机制** | 组合模式 | 将多个 Node 打包进同一进程，利用进程内通信（In-Process Communication）实现零拷贝 — C++ 内存管理的极佳场景 |
| **Lifecycle Nodes** | 状态模式 | 管理节点生命周期（Unconfigured → Inactive → Active → Finalized），比硬编码 if-else 优雅 |
| **Behavior Tree（行为树）** | 组合模式 | `behavior_path_planner` 是行为树在 L4 决策中落地的天花板，比有限状态机（FSM）更灵活 |
| **订阅/发布机制** | 观察者模式 | ROS 2 原生 DDS 通信的经典实现 |
| **Action 机制** | 命令模式 | 用于长时规划任务（如泊车），支持异步、可取消 |

**仿真安全冗余**：研究其 Planning 模块如何模仿 "Daruma" 式安全冗余模式、场景并行处理。

#### 2. Apollo (CyberRT) — 极致性能优化的硬核工业级教科书

Apollo 的 CyberRT 是纯 C++ 实现的高性能通信框架，适合高吞吐、低延迟场景的工程实践。

| 核心机制 | 对应设计模式 | 为什么值得看 |
|----------|-------------|-------------|
| **无锁队列 + 协程调度** | Producer-Consumer、Thread Pool | 干掉传统 OS 线程切换开销，C++ 高并发/多线程的终极演练场 |
| **共享内存通信** | — | 零拷贝数据流处理，理解 C++ 内存模型与屏障 |
| **插件机制** | 工厂模式 | Apollo 用宏 + 类工厂实现了类似 C++ 反射的功能，模块动态加载 |
| **规划/控制切换** | 策略模式 + 工厂模式 | 不同场景切换不同 Pipeline，基类 `Controller` → `MPCController` / `PIDController` |
| **各种 Manager** | 单例模式 | 全局管理器的经典用法 |
| **RSS 库集成** | — | 责任敏感安全模型的工程落地 |

---

### 基础设施层：工业级 C++ 极限形态

如果说 Autoware 和 Apollo 让你学会"如何组织一个庞大的自动驾驶系统"，那么 Folly、Poco 和 LLVM 就会让你明白"如何写出让机器运行速度达到物理极限的 C++ 代码"。

#### 3. Facebook Folly — 极致性能与高并发的天花板

互联网大厂为了榨干服务器最后一滴性能而产出的"现代 C++ 魔改库"。L4 车端计算平台（如 Nvidia Thor 或舱驾一体芯片）算力极其珍贵，Folly 里大量**无锁数据结构**和**原子操作的极端优化**，是打造高性能通信中间件（如优化 CyberRT、ROS2 DDS）的圣经。

| 核心机制 | 对应设计模式/优化 | 为什么值得看 |
|----------|------------------|-------------|
| **`folly::FBString`** | 动态策略模式 | 三种内存分配策略：极短字符串用栈（三指针大小）、中等用 SSO、长字符串才用堆。将"针对特定场景的性能策略"写进基础库的典范 |
| **`folly::Function`** | 多态 + 内存优化 | 比 `std::function` 更轻量，支持 move-only 语义，且没有小对象动态内存分配（No Small Object Allocation） |
| **`folly::MPMCQueue`** | 并发设计模式 | 极致优化的多生产者多消费者无锁队列，缓存行对齐（Cache-line alignment）防止伪共享 |
| **`folly::futex`** | 细粒度锁 | 比 `std::mutex` 在高并发下延迟更低，RAII 模式的极致应用 |

**核心学习点**：细粒度锁设计、缓存行对齐、RAII 极致应用、策略模式在内存管理中的落地。

#### 4. Poco — 经典的跨平台嵌入式"瑞士军刀"

一个结构极其严谨的 C++ 全功能类库（类似 C++ 版的 Java JDK）。在车载 Linux/QNX 等 RTOS（实时操作系统）中处理 HTTP 配置、日志、加密、多线程同步、XML/JSON 解析时，Poco 提供了近乎完美且轻量级的跨平台抽象。

| 核心机制 | 对应设计模式 | 为什么值得看 |
|----------|-------------|-------------|
| **`Poco::NotificationCenter` / `Poco::Events`** | 观察者模式 | 多线程环境下观察者模式的标准答案，通知与事件系统 |
| **`Poco::ClassLoader`** | 工厂模式 | 机器人/自动驾驶中"热插拔"传感器驱动或算法插件的典范。完美演示如何用 Factory 实现 C++ 动态插件加载 |
| **`Poco::ThreadPool`** | 命令模式 + 工作者模式 | 机器人异步任务管理的经典实现 |
| **整体架构** | GOF 23 种的教科书 | Poco 的代码极其端正，是学习经典设计模式在多线程/嵌入式场景下落地的首选 |

**核心学习点**：工程规范与架构、跨平台抽象、GOF 模式的工程落地。

#### 5. LLVM / Clang — 现代 C++ 编译器与全栈优化的圣经

现代计算机科学的奇迹。它不仅是一个编译器，更是**由无数优秀 C++ 设计模式堆叠起来的软件架构艺术品**。近两年（2025-2026）具身智能和大模型（VLM/World Model）上车极其火热——这些超大神经网络的高效部署严重依赖定制化 AI 编译器（基于 MLIR/LLVM 的 TVM、TensorRT 底层），懂得 LLVM 就拿到了 AI 算子极致优化和异构计算的入场券。

| 核心机制 | 对应设计模式 | 为什么值得看 |
|----------|-------------|-------------|
| **AST 遍历 / Pass 对 IR 的分析** | 访问者模式（终极演练） | 大量使用 Visitor 模式或其变体（如 `InstVisitor`）。这是处理复杂拓扑图（自动驾驶规划行为树、神经网络计算图）最高级的设计模式 |
| **`isa<>`, `cast<>`, `dyn_cast<>`** | 自定义 RTTI | LLVM 嫌弃 `dynamic_cast` 性能太差，自己用模板实现极致速度的运行时类型识别。处理高频图像/点云数据流的类型转换时有极高参考价值 |
| **类型系统 `llvm::Type` / 常量系统** | 享元模式 | 全局只保留一份实例，通过高效内存管理共享对象。适合处理大规模重复对象（如地图元素、点云特征） |

**核心学习点**：访问者模式在复杂图遍历中的工业级实现、模板元编程造 RTTI 轮子、享元模式在大规模对象管理中的应用。

---

## 二、其他高含金量开源项目

### 6. CARLA / esmini（仿真引擎 & OpenDrive 解析）

**推荐理由**：L4 核心痛点 — 安全和测试，数据驱动 + 场景仿真是近两年学术和工程热点。

| 值得挖掘 | 说明 |
|----------|------|
| **访问者模式** | 解析复杂的 OpenDrive XML 地图拓扑结构（车道线、路口 Junction） |
| **图论 + 智能指针** | 复杂拓扑结构在 C++ 中如何高效表达且不发生内存泄漏 |
| **解耦设计** | 仿真引擎各模块间的松耦合架构 |

### 7. NVIDIA TensorRT / TensorRT-LLM (C++ 部分)

**推荐理由**：端到端 / 大模型上车，高性能推理是工程落地唯一路径。

| 值得挖掘 | 说明 |
|----------|------|
| **构建者模式** | 构建 Network → Config → Engine 的完美链式调用 |
| **工厂模式** | 创建各种 Layer / Plugin |
| **自定义算子机制** | 多态 + 虚函数接口，将最新注意力机制（Attention）天衣无缝插入推理引擎 |

### 8. Google Cartographer（C++ 工程结构艺术品）

**推荐理由**：谷歌顶尖工程师堆出来的代码，结构严谨，堪称 C++ 艺术。

| 值得挖掘 | 说明 |
|----------|------|
| **Lua 动态配置 C++ 对象** | 经典的配置器模式 |
| **线程安全与内存屏障** | `std::mutex`、`std::unique_lock`、条件变量的教科书级应用 |
| **多传感器时间戳对齐** | 优雅处理并发数据同步 |

---

## 三、纵向对比：开源项目学习侧重点

为了不迷失在浩瀚的源码海洋里，用一张表理清学习侧重点和应用场景：

| 开源项目 | 核心设计模式/机制 | 在 L4/机器人中的映射 | 上手难度 |
|----------|------------------|---------------------|---------|
| **Autoware** | 组合模式、状态模式、观察者模式 | 系统架构与模块化设计 | ★★★☆☆ |
| **Apollo** | Producer-Consumer、策略模式、工厂模式 | 高性能通信中间件 | ★★★★☆ |
| **Folly** | 并发模式、无锁结构、策略模式（内存）、单例变体 | **性能压榨**：优化车端数据中间件（通信、线程调度、内存池） | ★★★★☆ |
| **Poco** | 观察者模式、工厂模式、命令模式 | **工程规范与架构**：规范机器人系统框架、设备通信、插件动态加载 | ★★★☆☆ |
| **LLVM** | 访问者模式、享元模式、组合模式、自定义 RTTI | **异构计算与 AI 编译**：端到端大模型在边缘端的算子融合、高性能图优化 | ★★★★★ |
| **CARLA/esmini** | 访问者模式 | 仿真与地图解析 | ★★★☆☆ |
| **TensorRT** | 构建者模式、工厂模式 | AI 推理引擎 | ★★★☆☆ |
| **Cartographer** | 配置器模式、线程安全 | SLAM 与传感器融合 | ★★★☆☆ |

**推荐学习顺序**：Poco（培养规范 OO 架构思维）→ Autoware（理解大型系统组织）→ Apollo（攻克高并发通信）→ Folly（性能压榨进阶）→ LLVM（编译器与异构计算终极挑战）。

---

## 四、跨界缝合：如何交叉内化

将这些底层知识内化为自己的学术与工程能力，尝试做以下"跨界缝合"：

### 1. 用 Folly 的思想去重构 Apollo 的通信

去看看 Apollo CyberRT 里的循环队列（Lock-Free Queue），对比 `folly::MPMCQueue`。思考 Folly 的 `folly::futex` 是如何做到比 `std::mutex` 在高并发下延迟更低的？能否把这种极致的无锁并发引入到自动驾驶的多传感器融合时间戳对齐模块中？

### 2. 用 Poco 的规范去写 Autoware 的插件系统

Autoware Universe 的 Component 机制很优秀。尝试用 Poco 的 `ClassLoader` 和 `Manifest` 机制，自己写一个微型的、支持跨平台（Windows/Linux/QNX）的机器人传感器驱动加载框架。

### 3. 用 LLVM 的 Visitor 模式去处理自动驾驶的地图与场景

在 L4 级自动驾驶中，高精地图（HD Map）通常表现为复杂的车道拓扑图（Vector Map）。如何高效地遍历这些车道、计算最短路径、判断换道可行性？LLVM 遍历 IR 图（Intermediate Representation）的 Visitor 模式和数据流分析（Data-Flow Analysis）思想，可以直接迁移到自动驾驶的**全局路径规划（Routing）算法架构**中。

---

## 五、进阶路线：逆向工程法

不要死记硬背《Head First 设计模式》，用"三步逆向法"：

### 步骤 1：发现痛点

看 Apollo 的控制模块，思考：

> 如果有 10 种不同车模型、5 种不同控制算法（MPC / PID / LQR），不用设计模式，代码会变成什么样？
>
> → 全是 if-else，改一处错全局。

### 步骤 2：源码对照

看 Apollo 如何定义基类 `Controller`，然后利用 Factory 模式根据配置文件动态 `new` 出具体的 `MPCController`。

> 这就是**策略模式 + 工厂模式**的完美结合。

### 步骤 3：动手造轮子

用自己的代码验证理解：
- 用纯 C++20 写一个精简版 "Mini-CyberRT" 通信框架
- 写一个基于行为树的简易自动泊车决策器
- 用 Poco ClassLoader 写一个跨平台传感器热插拔框架

---

## 六、书籍与论文推荐

### 工程骨架（C++）

| 书籍 | 用途 |
|------|------|
| 《Effective Modern C++》 — Scott Meyers | 搞懂 C++11/14/17 的内存与性能优化 |
| 《C++ Concurrency in Action》 — Anthony Williams | 看懂 CyberRT / Folly 高并发源码的唯一圣经 |
| 《C++ Templates: The Complete Guide》 | 理解 LLVM 自定义 RTTI（`isa<>`, `cast<>`）的模板基础 |

### 设计模式

| 书籍 | 用途 |
|------|------|
| 《Head First 设计模式》 | 入门首选，图文并茂 |
| 《Design Patterns》 — GoF 四人帮 | 经典原著，读完后对照 Poco / Autoware / Apollo 会大呼过瘾 |

### 学术与工程前沿（2024–2026）

- **IEEE T-IV** (Transactions on Intelligent Vehicles)
- **CVPR / ICRA / IROS** — 近两年 "端到端自动驾驶" 与 "World Model" 相关
- 重点关注：高性能 C++ 在边缘端（Nvidia Orin / Thor）的落地架构
- **LLVM / MLIR** 相关论文：AI 编译器在车载 NPU/GPU/DSP 的异构部署

---

## 学习清单

### 应用层
- [ ] Autoware — Component 机制 & 进程内通信
- [ ] Autoware — Lifecycle Nodes（状态模式）
- [ ] Autoware — Behavior Tree（组合模式）
- [ ] Apollo — CyberRT 无锁队列 & 协程调度
- [ ] Apollo — 插件机制（工厂模式 + 宏反射）
- [ ] Apollo — 规划/控制 Pipeline（策略模式）

### 基础设施层
- [ ] Folly — FBString 动态策略模式
- [ ] Folly — MPMCQueue 无锁队列 & 缓存行对齐
- [ ] Folly — Function 多态 + 小对象优化
- [ ] Poco — NotificationCenter 观察者模式
- [ ] Poco — ClassLoader 动态插件加载
- [ ] Poco — ThreadPool 命令模式 + 工作者模式
- [ ] LLVM — Visitor 模式遍历 AST / IR
- [ ] LLVM — 自定义 RTTI（`isa<>`, `cast<>`, `dyn_cast<>`）
- [ ] LLVM — 享元模式（类型系统 / 常量系统）

### 其他项目
- [ ] CARLA / esmini — 访问者模式解析 XML
- [ ] TensorRT — 构建者模式 & 自定义算子
- [ ] Cartographer — Lua 动态配置 & 线程安全

### 造轮子
- [ ] Mini-CyberRT 通信框架（纯 C++20）
- [ ] 行为树简易自动泊车决策器
- [ ] 基于 Poco ClassLoader 的跨平台传感器热插拔框架

### 阅读
- [ ] 《Effective Modern C++》精读
- [ ] 《C++ Concurrency in Action》精读
- [ ] 《C++ Templates: The Complete Guide》— LLVM RTTI 前置
- [ ] 跟踪 IEEE T-IV / CVPR 端到端自动驾驶前沿

---

*记录于 hermes_brainstorm · topics/cpp/*
