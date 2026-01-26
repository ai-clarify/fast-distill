# FastDistill 架构问题分析

日期：2026-01-26

## 范围
本文聚焦 FastDistill 当前架构在可维护性、可靠性、演进性方面的设计问题。
分析依据当前代码结构与实现，例如：`src/fastdistill/pipeline/base.py`、
`src/fastdistill/steps/base.py`、`src/fastdistill/mixins/runtime_parameters.py` 等。

## 摘要结论
- 编排层职责过重，执行/缓存/存储/日志深度耦合。
- 全局可变状态（pipeline context、CUDA 设备分配）带来并发脆弱性。
- Runtime 参数依赖 Pydantic 内部字段，已产生弃用告警。
- 序列化与缓存缺少显式版本协议，升级风险高。
- Lazy import 广泛使用，增加调试与工具链复杂度。

## 关键问题

### 1）编排层过于“单体化”
**证据**：`src/fastdistill/pipeline/base.py` 近 1900 行，涵盖执行、缓存、
文件系统传输、序列化、队列与日志等多项职责。

**影响**
- 高耦合：缓存或执行策略变更会触及核心编排逻辑。
- 测试困难：关键行为只能通过昂贵的集成测试验证。
- 演进缓慢：引入新执行后端必须理解大量隐式约束。

**建议路径**
- 抽象 `ExecutionEngine`、`CacheManager`、`StorageBackend` 等接口。
- `BasePipeline` 聚焦 DAG 组合与生命周期，具体执行委托给引擎。
- 明确层间数据契约，降低横向联动。

---

### 2）全局可变状态与环境耦合
**证据**：`_GlobalPipelineManager` 与 `CudaDevicePlacementMixin` 使用
进程级全局状态与主机临时文件，同时修改 `CUDA_VISIBLE_DEVICES`。

**影响**
- 同进程多 pipeline 并发时容易相互干扰。
- CI/测试环境下的可复现性降低。
- 环境变量副作用难以追踪与回滚。

**建议路径**
- 采用显式的 execution context（随 pipeline 传递）替代全局上下文。
- CUDA 设备分配改为“策略对象”，与 pipeline 实例绑定。
- 将环境变量修改收敛到单一执行边界。

---

### 3）Runtime 参数依赖 Pydantic 内部实现
**证据**：`RuntimeParametersMixin` 迭代 `self.model_fields`，当前测试已
出现 Pydantic 弃用告警。

**影响**
- Pydantic 升级后可能直接失效。
- 警告噪声掩盖真实问题。
- 运行时反射过多，复杂度与成本偏高。

**建议路径**
- 改用类级字段（`self.__class__.model_fields`）。
- 在类构建阶段缓存 runtime 参数元数据。
- 长期考虑脱离 Pydantic 内部细节的轻量 schema 层。

---

### 4）序列化与缓存缺少显式版本协议
**证据**：自定义 `_Serializable` 仅携带 `type_info`，未包含 schema 版本
或迁移逻辑。

**影响**
- 版本升级后缓存不兼容风险高。
- Pipeline / Step 持久化对象难以迁移。

**建议路径**
- 序列化数据增加 `schema_version` 字段。
- 建立迁移注册表，支持跨版本升级。
- 将运行时缓存与长期配置数据分离。

---

### 5）控制面与数据面耦合过深
**证据**：Step 直接依赖 pipeline 上下文；许多策略与观测逻辑分散在步骤内。

**影响**
- Step 复用难度高，脱离 pipeline 即不可用。
- 质量/观测策略偏“隐式”，难以统一治理。

**建议路径**
- 设计最小执行上下文接口，作为 Step 的唯一依赖。
- 将质量与观测策略提升为控制面配置。
- 将关键观测输出固化为 pipeline 级合同。

---

### 6）Lazy import 机制过度分散
**证据**：`fastdistill`、`fastdistill.steps`、`fastdistill.models` 等多个
包通过 `__getattr__` 做字符串映射 lazy import。

**影响**
- IDE 与静态分析体验差。
- import 行为难预测，调试成本高。
- 对插件化扩展的支持分散且不统一。

**建议路径**
- 将 lazy import 收敛到顶层 API。
- 采用统一 registry / entry-point 机制。
- 将动态映射逻辑集中管理并标准化。

---

### 7）存储与批传输策略嵌入核心流程
**证据**：`BasePipeline` 持有 `_BatchManager`/`_WriteBuffer` 并内置
`use_fs_to_pass_data` 分支。

**影响**
- 性能优化必须改动核心编排逻辑。
- 对 S3/Ray Object Store 等后端支持不自然。

**建议路径**
- 引入 `BatchTransport` 接口（内存/文件系统/对象存储）。
- 让传输策略成为 pipeline 配置，而非内部条件分支。

---

### 8）测试成本高反映出架构重量
**证据**：集成测试耗时长，很多行为只能通过完整 pipeline 执行验证。

**影响**
- 反馈慢，CI 成本高。
- 不利于架构级重构与验证。

**建议路径**
- 将编排拆解为可单测的组件。
- 引入 fast/smoke 套件，重测试改为夜间运行。

## 需要保留的优势
- 明确区分“数据生成”与“训练”（模型平面外置）。
- Manifest / Quality / Timing 报告已是一级产物。
- Step 库丰富、模型适配面广。

## 建议的优先行动
1. 先拆 execution engine 与 storage backend，降低 `BasePipeline` 复杂度。
2. 为序列化增加 schema 版本与迁移链路。
3. 移除全局 pipeline context，采用显式上下文。
4. 统一 lazy import 与插件注册机制。

