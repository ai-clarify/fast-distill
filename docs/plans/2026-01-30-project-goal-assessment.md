# 项目目标评估：Fast Distill

> 日期: 2026-01-30
> 状态: 评估完成

## 评估范围

对 Fast Distill 项目的目标清晰度、合理性、风险点进行系统审视，基于当前代码库（v1.5.3, ~40K 行）、架构文档、5 轮 baseline 数据和工程实践。

---

## 1. 目标清晰度：高

项目的四个硬约束定义精确，彼此无矛盾，且每个都有对应实现模块：

| 硬约束 | 实现支撑 |
|--------|----------|
| 最大化 Teacher 吞吐，不降低质量下限 | BatchManager + 多 Provider 并发 + 三级质量门控 |
| 质量门控可证伪、可重放 | Rule → Exec → Judge 三级门控；`sample_id = sha256(task_id + canonical_input)` 确定性契约 |
| 训练与数据生成解耦 | Control / Data / Model 三平面分离，训练在 data-generation 路径之外 |
| 可审计、可复现 | manifest + quality report + timing report 构成完整可观测体系 |

**结论**：目标层面不存在模糊定义或自相矛盾的问题。

---

## 2. 目标合理性：合理，但需场景锚定

### 2.1 合理的部分

- **定位精准**：只做"数据蒸馏"这一段，不做全栈训练框架。scope 控制好，避免与 distilabel / axolotl 全面竞争
- **架构决策正确**：Provider 适配层 + 确定性契约 + 三级质量门控，工程上可维护
- **已有基线验证**：5 轮 WikiSQL benchmark 跑通，exec_pass 0.93–0.99，核心链路可工作
- **可观测性一流**：manifest / quality / timing 三份报告作为 first-class citizen，同类项目中少见

### 2.2 Baseline 数据摘要

| Run | 场景 | Teacher | exec_pass | gold_match | judge_score |
|-----|------|---------|-----------|------------|-------------|
| 1 | WikiSQL 1k | DeepSeek V3.2 | 0.929 | 0.309 | 0.619 |
| 2 | WikiSQL 1k + CleanSqlOutput | DeepSeek V3.2 | 0.986 | 0.449 | 0.7175 |
| 3 | WikiSQL 200 gold-match-only | DeepSeek V3.2 | — | 0.29 (student) | 1.0 (distilled) |
| 4 | Ollama smoke 2-sample | qwen3:0.6b | 1.0 | 0.5 | 0.75 |
| 5 | OpenRouter smoke 2-sample | DeepSeek V3.2 | 1.0 | 1.0 | — |

数据证明：质量门控有效提升 distilled 数据质量；CleanSqlOutput 带来显著提升（exec_pass 0.929→0.986）。

---

## 3. 风险点

### 3.1 代码体量 vs 验证场景的匹配度

40K+ 行代码、11 个模块、14 个 optional extras。对 Beta 项目偏重。

**核心问题**：目前只有 Text2SQL (WikiSQL) 一个验证场景，但架构已为多场景做了大量泛化。如果最终只有 Text2SQL 跑得通，现有泛化设计即为过度工程。

**建议**：在 Text2SQL 之外再跑通 1–2 个场景（代码生成、数学推理），验证架构泛化能力后再决定是否继续扩展抽象层。

### 3.2 质量门控的泛化性

Exec Eval 当前紧耦合 SQLite 执行（`SQLiteExecEval`）。对于代码生成需要 sandbox runner，数学推理需要 answer extraction + symbolic comparison。架构文档提及但尚未落地。

**建议**：下一阶段优先实现一个非 SQL 的 ExecEval（如 Python code sandbox），验证 exec 层的可扩展性。

### 3.3 Student 训练效果的归因难度

Baseline 中 gold_match 最高 0.449（Run 2），student post-train judge_score ~0.72。数据质量门控有效，但 student 最终效果还受 LoRA rank、学习率、数据量等训练超参影响——这些不在项目 scope 内。

**风险**：用户可能将 student 表现不佳归因于蒸馏质量，而实际瓶颈在训练侧。

**建议**：文档中明确标注"训练超参对最终效果的影响"，给出推荐的训练配置作为参考，降低用户归因误判。

### 3.4 多 Provider 维护成本

支持 OpenAI / Ollama / vLLM / SGLang / Cohere / Groq 等，每个都有边界情况（如 OpenRouter JSON 截断问题）。

**建议**：按实际用量分级——Tier 1（OpenAI-compatible / Ollama）保证全测试覆盖，Tier 2（其余 Provider）社区贡献 + best-effort 维护。

---

## 4. 总结

| 维度 | 评级 | 说明 |
|------|------|------|
| 目标清晰度 | ★★★★★ | 四个硬约束定义精确，无矛盾 |
| 目标合理性 | ★★★★☆ | 方向正确，但泛化声明需更多场景验证 |
| 架构匹配度 | ★★★★☆ | 模块化好，但复杂度对 Beta 偏高 |
| 验证充分性 | ★★★☆☆ | 仅 Text2SQL 一个场景完整跑通 |
| 工程实践 | ★★★★★ | CI/CD、可观测性、error-experience 体系完善 |

**核心结论**：方向对，scope 需要用更多场景验证来锚定。

---

## 5. 下一步行动项

- [ ] 选定第二个验证场景（代码生成 / 数学推理），设计 pipeline 并跑通 baseline
- [ ] 实现一个非 SQL 的 ExecEval，验证 exec 层可扩展性
- [ ] 对现有模块做一次"减法审计"，识别未被用户路径覆盖的代码
- [ ] 在文档中补充训练超参对 student 效果的影响说明
- [ ] 确定 Provider 分级策略（Tier 1 / Tier 2）
