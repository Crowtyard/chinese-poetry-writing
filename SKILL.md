---
name: chinese-poetry-writing
description: 中文诗歌创作方法 Skill，负责中文诗歌的构思、创作、批评、修订与全流程调度；适用于写诗、作诗、五绝、七绝、古诗、格律诗、命题诗、润色诗、改诗、点评诗稿等请求。仅查询押韵、平仄、韵部、合律或多音字读音时，应交给 chinese-poetry-prosody。
metadata:
  version: "0.1-beta"
---

# chinese-poetry-writing —— 中文诗歌创作方法 Skill（v0.1-beta）

## 名称与版本

- skill_name: chinese-poetry-writing
- version: v0.1-beta
- 性质：BETA。提供已验证的方法，不宣称审美模型已经客观完备。
- 集成状态：v0.1-beta + MINIMUM_PRODUCT_INTEGRATION_V1（运行时教学资产已接入
  `references/runtime_teaching/`，接入范围与档位见「Runtime Teaching」一节）。

## 职责（COMPOSE / CRITIQUE / REVISE / ORCHESTRATE）

- COMPOSE：如何发现诗眼、如何构思、如何成稿。
- CRITIQUE：如何批评诗稿（自查与他评共用同一纪律）。
- REVISE：如何修改（先保什么、后动什么、何时回退）。
- ORCHESTRATE：全流程调度、迭代上限、输出纪律。

本 Skill 不绑定任何具体 Persona。小光、Kun 及其他角色均可调用。

## 职责边界

| 层 | 负责 |
|---|---|
| Persona（角色） | 人格、经历、视角、声音（永不并入本 Skill） |
| Writing Skill（本文件） | 写诗的方法：发现→构思→成稿→批→改 |
| chinese-poetry-prosody | 确定性验律（拼音/平仄/押韵/相对/相粘/韵部），独立存在 |

## 触发条件

用户要求以下任一时可加载本 Skill：
写诗、作诗、写五绝、写七绝、写古诗、写格律诗、命题诗、润色诗、改诗、批评/点评诗稿、要求完整创作工作流。

以下情况**不**进入创作流程，优先转交 chinese-poetry-prosody：
仅查询押韵、查平仄、查韵部、验某诗是否合律、多音字读音——由 chinese-poetry-prosody 处理。

## 调度流程（ORCHESTRATE）

```
USER_REQUEST
↓
PREMISE STATUS CHECK（条件式，非必经 Gate；细则见 protocols/orchestration.md 步骤 0）
  输入已含具体处境／关系／stake → 继续（跳过 Formation）
  否则 → 轻量初始 Discovery 探针
    Discovery 已带 stake → 继续
    仍是纯观察 → PREMISE_FORMATION（references/runtime_teaching/premise_formation.md）
    找不到自然 Premise → NO_POEM_DIRECTION（合法出口，不编故事）
↓
COMPOSE
  FACT
  IRREPLACEABLE_FACT
  DISCOVERY（≥3）
  RELATION
  CONCEPTS（2-3）
  DRAFT
↓
CRITIQUE（EVIDENCE / RELATION / NATURALNESS / EXPLANATION /
         TECHNIQUE_VISIBILITY / IRREPLACEABILITY）
↓
REVISE
↓
调用 chinese-poetry-prosody 验律
↓
如格律有问题 → REVISE（只动违规处，保诗眼）→ 复检
↓
FINAL_AESTHETIC_CHECK（修律后重过 CRITIQUE 核心项）
↓
OUTPUT
```

- 内部分析（FACT/DISCOVERY/CRITIQUE 过程）默认不展示给用户；仅输出诗与必要说明。
- 迭代上限：构思 ≤3 轮；批评-修订 ≤3 轮；修律 ≤5 轮。不收敛则如实报告 UNRESOLVED。

## Runtime Teaching（MINIMUM_PRODUCT_INTEGRATION_V1）

资产目录：`references/runtime_teaching/`（critic 校准资产 + premise formation 压缩资产）。
执行协议仍只有 `protocols/critique.md`；该目录是被取用的材料，不是规则清单。

纪律：**DEFAULT AVAILABLE ≠ LOAD EVERYTHING**。按当前诊断问题只取最相关的一项，不整包加载；
`failure_index_retrieval.md` 只是案例检索索引，**绝不**作为逐项 checklist。

| 档位 | 何时 | 加载 |
|---|---|---|
| MINIMAL | 普通批评／交付前自查 | critique protocol + 最相关的 1 个 contrast |
| STANDARD | 已有明确怀疑方向 | 1-2 个相关 contrast；仅怀疑打油感／散文压缩时才加 critic_acoustics.md |
| DEEP | 疑难、多轮不收敛、需历史近似案例校准 | 允许检索 failure_index_retrieval.md + 多个 contrast |

- Critic 有三档合法判决，`NO_MATERIAL_PROBLEM` 合法；`LOCAL_RISK != POEM_FAILURE`；
  过度解释受 `INTERPRETIVE_OVERREACH_GUARD` 约束（细则见 protocols/critique.md）。
- Premise Formation 是**条件式**步骤：仅当裸题且初始 Discovery 仍是纯观察时调用；
  用户输入已含具体处境／关系／stake，或 Discovery 自身已带 stake → 跳过。
  找不到自然 Premise → 允许 `NO_POEM_DIRECTION`，不编故事。
- **未接入（保持实验态）**：Composer Teaching、Reviser Trajectory Teaching
  （`COMPOSER_TEACHING = EXPERIMENTAL_NOT_RUNTIME`／`REVISER_TEACHING = EXPERIMENTAL_NOT_RUNTIME`）。
  研究仓文件存在也不自动读取。既有原则继续有效：`POETIC_EYE_PRESERVED`；修律可撤回（prosody repair may be rolled back）。

## Prosody 集成

- 完成审美稿后调用已安装的 `chinese-poetry-prosody`；个人级 Codex Skill 默认放在 `$HOME/.agents/skills/chinese-poetry-prosody/`。
- 调用方式（以其 SKILL.md 为准）：
  `py scripts/check_poem.py --poem "<诗>" [--form jueju5|jueju7] [--reading 行:列=拼音] [--rhyme-profile xinyun18]`
- 判定：PASS 可交付；WARN 按提示决定是否处理；FAIL 必须修订对应句后复检。
- 本 Skill 不复制、不内嵌 Prosody 的拼音/平仄/押韵/相对/相粘/韵部判定逻辑，不复制 chars.json；
  不修改 chinese-poetry-prosody。LLM 不自行猜判声韵，一切以脚本报告为准。

## 用户偏好层（SOFT，默认通用模式）

- 默认**通用模式**：不强制应用任何单一用户的偏好。写诗以诗本身成立为准
  （物证在场、关系做功、语言自然、不解释诗眼、不强行象征）。
- 仅当上下文明确属于提供偏好的该用户（或其明示采用该偏好集）时，参考
  `references/user_soft_preferences.md`。
- 无论是否启用偏好层，下列都**不是硬规则**：无「的」、有动态关系、短句、对称、
  白描、无古典词。它们最多是倾向，不得作为通过/不通过的判据。
- 「的」按 HIGH_COST_FUNCTION_WORD 处理（六问），不是禁词。

## 结构地图

- protocols/compose.md｜critique.md｜revise.md｜orchestration.md —— 执行细则
- references/poetic_discovery.md｜relational_imagery.md｜omission_vs_missing.md｜
  endings.md｜bad_poetry_patterns.md｜user_soft_preferences.md —— 判据与速查
- references/runtime_teaching/ —— critic_contrasts.md｜critic_acoustics.md｜
  failure_index_retrieval.md｜premise_formation.md —— 运行时教学资产（按档位取用，不整包加载）
- examples/liked_examples.md｜failure_examples.md —— 真人裁决样本（可学不可抄）
- tests/smoke_cases.md —— 冒烟用例清单（v0.1-beta 验收）
