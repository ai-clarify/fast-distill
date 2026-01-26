# Distillation Papers (curated)

A reading list tuned for FastDistill. Each paper includes a short method snapshot and a concrete note on whether/how it can be used to optimize this repo.

**Feasibility rubric**
- **High**: integrates with the current data pipeline or needs only minor extensions.
- **Medium**: needs extra artifacts (logprobs, preferences) or self-hosted teachers.
- **Low**: requires hidden states/gradients or heavy training-loop changes.

## Foundational KD

| Paper | Method snapshot | FastDistill optimization path | Feasibility | Link |
| :-- | :-- | :-- | :-- | :-- |
| Distilling the Knowledge in a Neural Network | Soft targets with temperature to transfer teacher distribution. | Capture teacher logprobs in generation artifacts; train with KL to soft targets. | Medium | https://arxiv.org/abs/1503.02531 |
| FitNets: Hints for Thin Deep Nets | Distill intermediate representations (“hints”). | Add optional hidden-state capture for self-hosted teachers; align layer outputs. | Low | https://arxiv.org/abs/1412.6550 |
| Born Again Neural Networks | Self-distillation: student becomes new teacher. | Make iterative runs first-class (run_id chain + teacher swap) to bootstrap students. | High | https://proceedings.mlr.press/v80/furlanello18a.html |
| LIT: Block-wise Intermediate Representation Training | Block-wise intermediate matching with teacher block inputs. | Only feasible with self-hosted teachers that expose block outputs. | Low | https://arxiv.org/abs/1810.01937 |

## Transformer KD

| Paper | Method snapshot | FastDistill optimization path | Feasibility | Link |
| :-- | :-- | :-- | :-- | :-- |
| DistilBERT | Distillation during pretraining with MLM + KD + cosine loss. | Use as student pretraining recipe; requires teacher hidden states. | Medium | https://arxiv.org/abs/1910.01108 |
| Patient KD for BERT | Distill multiple intermediate layers (PKD-Last/PKD-Skip). | Add multi-layer alignment if teacher is self-hosted. | Medium | https://arxiv.org/abs/1908.09355 |
| TinyBERT | Transformer-specific distillation at pretrain + task stages. | Use as student training recipe; needs attention/hidden states. | Medium | https://arxiv.org/abs/1909.10351 |
| MiniLM | Distill self-attention relations (QK + value relations). | Implement if training stack can access attention maps. | Medium | https://arxiv.org/abs/2002.10957 |
| MiniLMv2 | Multi-head self-attention relation distillation without head constraints. | Same as MiniLM, but more flexible head counts. | Medium | https://arxiv.org/abs/2012.15828 |

## LLM KD

| Paper | Method snapshot | FastDistill optimization path | Feasibility | Link |
| :-- | :-- | :-- | :-- | :-- |
| Distilling Step-by-Step! | Use rationales as extra supervision for small models. | Add rationale generation + gating; store rationale fields for multi-task training. | High | https://aclanthology.org/2023.findings-acl.507/ |
| MiniLLM | Reverse-KL KD for generative LMs. | Capture teacher logprobs and use reverse-KL; combine with SFT on curated outputs. | Medium | https://arxiv.org/abs/2306.08543 |
| DistiLLM | Skew-KL KD + adaptive off-policy sampling. | Add off-policy student generations and mix with teacher data for training. | Medium | https://arxiv.org/abs/2402.03898 |
| Direct Preference KD | Preference-based KD using implicit reward + reverse KL. | Reuse judge/reward model outputs to build preference pairs for student training. | Medium | https://arxiv.org/abs/2406.19774 |

## Dataset distillation & data distillation

| Paper | Method snapshot | FastDistill optimization path | Feasibility | Link |
| :-- | :-- | :-- | :-- | :-- |
| Data Distillation | Self-training with multi-transform pseudo-labels. | Add multi-prompt / multi-decode pseudo-labeling for unlabeled data. | High | https://arxiv.org/abs/1712.04440 |
| Dataset Distillation | Optimize synthetic data via gradient matching. | Not suitable for black-box teachers; needs differentiable training loop. | Low | https://arxiv.org/abs/1811.10959 |
| Matching Training Trajectories | Distill by matching parameter trajectories. | Requires storing training trajectories; heavy training integration. | Low | https://arxiv.org/abs/2203.11932 |
| Deep Generative Prior | Use generative priors to synthesize distilled data. | Better fit for vision tasks; less direct for text-only pipelines. | Low | https://arxiv.org/abs/2305.01649 |
| DiLM: Dataset Distillation with Language Models | Train an LM to generate distilled text samples. | Train a small generator on curated data; plug into data synthesis step. | Medium | https://aclanthology.org/2024.findings-naacl.199/ |

## Surveys (for evaluation checklists)

| Paper | What to reuse | Feasibility | Link |
| :-- | :-- | :-- | :-- |
| A Survey on KD of LLMs | Taxonomy + evaluation checklist for FastDistill runs. | High | https://arxiv.org/abs/2402.13116 |
| Survey on KD for LLMs | Method categories + evaluation tasks for benchmark planning. | High | https://arxiv.org/abs/2407.01885 |
