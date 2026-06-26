# C++ 设计模式学习路径

> 核心理念：**逆向工程法** — 不要死记硬背模式定义，而是从优秀开源项目中反向识别"为什么这里用了这个模式"。
>
> 小项目 > 大项目。代码量少才能快速看清全局结构。

---

## 一、推荐深度挖掘的项目

### 1. Autoware (ROS 2 / Universe) — SOA 与现代 C++ 教科书

Autoware Universe 大量使用 C++17/20，是学习面向服务架构（SOA）在实时系统中落地的绝佳素材。

| 核心机制 | 对应设计模式 | 为什么值得看 |
|----------|-------------|-------------|
| **Component 组件机制** | 组合模式 | 将多个 Node 打包进同一进程，利用进程内通信（In-Process Communication）实现零拷贝 — C++ 内存管理的极佳场景 |
| **Lifecycle Nodes** | 状态模式 | 管理节点生命周期（Unconfigured → Inactive → Active → Finalized），比硬编码 if-else 优雅 |
| **Behavior Tree（行为树）** | 组合模式 | `behavior_path_planner` 是行为树在 L4 决策中落地的天花板，比有限状态机（FSM）更灵活 |
| **订阅/发布机制** | 观察者模式 | ROS 2 原生 DDS 通信的经典实现 |
| **Action 机制** | 命令模式 | 用于长时规划任务（如泊车），支持异步、可取消 |

**仿真安全冗余**：研究其 Planning 模块如何模仿 "Daruma" 式安全冗余模式、场景并行处理。

### 2. Apollo (CyberRT) — 极致性能优化的硬核工业级教科书

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

## 二、其他高含金量开源项目

### 3. CARLA / esmini（仿真引擎 & OpenDrive 解析）

**推荐理由**：L4 核心痛点 — 安全和测试，数据驱动 + 场景仿真是近两年学术和工程热点。

| 值得挖掘 | 说明 |
|----------|------|
| **访问者模式** | 解析复杂的 OpenDrive XML 地图拓扑结构（车道线、路口 Junction） |
| **图论 + 智能指针** | 复杂拓扑结构在 C++ 中如何高效表达且不发生内存泄漏 |
| **解耦设计** | 仿真引擎各模块间的松耦合架构 |

### 4. NVIDIA TensorRT / TensorRT-LLM (C++ 部分)

**推荐理由**：端到端 / 大模型上车，高性能推理是工程落地唯一路径。

| 值得挖掘 | 说明 |
|----------|------|
| **构建者模式** | 构建 Network → Config → Engine 的完美链式调用 |
| **工厂模式** | 创建各种 Layer / Plugin |
| **自定义算子机制** | 多态 + 虚函数接口，将最新注意力机制（Attention）天衣无缝插入推理引擎 |

### 5. Google Cartographer（C++ 工程结构艺术品）

**推荐理由**：谷歌顶尖工程师堆出来的代码，结构严谨，堪称 C++ 艺术。

| 值得挖掘 | 说明 |
|----------|------|
| **Lua 动态配置 C++ 对象** | 经典的配置器模式 |
| **线程安全与内存屏障** | `std::mutex`、`std::unique_lock`、条件变量的教科书级应用 |
| **多传感器时间戳对齐** | 优雅处理并发数据同步 |

---

## 三、进阶路线：逆向工程法

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

---

## 四、书籍与论文推荐

### 工程骨架（C++）

| 书籍 | 用途 |
|------|------|
| 《Effective Modern C++》 — Scott Meyers | 搞懂 C++11/14/17 的内存与性能优化 |
| 《C++ Concurrency in Action》 — Anthony Williams | 看懂 CyberRT 高并发源码的唯一圣经 |

### 设计模式

| 书籍 | 用途 |
|------|------|
| 《Head First 设计模式》 | 入门首选，图文并茂 |
| 《Design Patterns》 — GoF 四人帮 | 经典原著，读完后对照 Autoware / Apollo 会大呼过瘾 |

### 学术与工程前沿（2024–2026）

- **IEEE T-IV** (Transactions on Intelligent Vehicles)
- **CVPR / ICRA / IROS** — 近两年 "端到端自动驾驶" 与 "World Model" 相关
- 重点关注：高性能 C++ 在边缘端（Nvidia Orin / Thor）的落地架构

---

## 学习清单

- [ ] Autoware — Component 机制 & 进程内通信
- [ ] Autoware — Lifecycle Nodes（状态模式）
- [ ] Autoware — Behavior Tree（组合模式）
- [ ] Apollo — CyberRT 无锁队列 & 协程调度
- [ ] Apollo — 插件机制（工厂模式 + 宏反射）
- [ ] Apollo — 规划/控制 Pipeline（策略模式）
- [ ] CARLA / esmini — 访问者模式解析 XML
- [ ] TensorRT — 构建者模式 & 自定义算子
- [ ] Cartographer — Lua 动态配置 & 线程安全
- [ ] 造轮子：Mini-CyberRT 通信框架
- [ ] 造轮子：行为树简易自动泊车决策器
- [ ] 《Effective Modern C++》精读
- [ ] 《C++ Concurrency in Action》精读
- [ ] 跟踪 IEEE T-IV / CVPR 端到端自动驾驶前沿

---

*记录于 hermes_brainstorm · topics/cpp/*
