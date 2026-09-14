# protocols/orchestration.md —— 编排协议（v0.1-beta / STEP 2）

把 compose / critique / revise / 外部 prosody 串成一条可执行流水线，并规定循环上限与角色边界。

## 角色边界

- Persona / LLM 调用方：人格、经历、视角、声音；提供题目或素材。永不并入本 Skill。
- chinese-poetry-writing：方法（发现→成稿→自查→修订）。本层不内嵌任何拼音/平仄/韵部数据。
- chinese-poetry-prosody：唯一验律方（外部 CLI，只读判定）。本层只负责成稿后调用、按报告修律、复检。

## 标准工作流（前置条件检查 + 11 步）

### 步骤 0 · PREMISE STATUS CHECK（条件式，非必经 Gate）

```text
INPUT
↓
输入已含具体处境／关系／stake／meaningful tension？
├─ YES → 继续（跳过 Premise Formation）
└─ NO（裸题）→ 轻量初始 Discovery 探针
     ├─ Discovery 自身已带 stake → 继续（MAY_SKIP）
     ├─ 仍是纯现象／观察 → PREMISE_FORMATION
     │     细则与三问验收：references/runtime_teaching/premise_formation.md
     │     ├─ 找到自然 Premise → 继续（FACT 搜索以该处境／关系为方向）
     │     └─ 找不到 → NO_POEM_DIRECTION（合法出口：如实报告，不写诗，不编故事）
     └─（可选诊断）PREMISE_GATE 仅用于「Discovery 很聪明，但说不清为什么值得写」的疑难情况
```

- `PREMISE_GATE = OPTIONAL_DIAGNOSTIC`：**不是** mandatory node，不参与通过／不通过判定，不产生阻断，
  也不得替代 Discovery。
- Formation 产物**不得**自动否决已带 stake 的 Direct Discovery（历史上有真人选 Direct 胜出的样本）。
- 本节点不改变后续步骤编号；跳过时流水线行为与 v0.1-beta 一致。

### 步骤 0.5 · AFFECTIVE INTENT（写作准备步骤，非 Gate）

```text
（PREMISE STATUS CHECK 之后）
↓
AFFECTIVE INTENT —— 只回答三问：
  ① 这个具体题材／处境中，真正触动人的是什么？
  ② 从这个处境自然生长出来的主要思想感情是什么？
  ③ 哪些事实、动作、关系、物象能够承载这种感情，而不必把感情直接解释出来？
↓
产物 = 一句内部写作方向
├─ 自然形成 → 进入 COMPOSE（FACT／DISCOVERY／RELATION／CONCEPT 均受其约束）
├─ 情感很轻但真实 → 同样合法，照此写，不升格、不加重
└─ 找不到自然方向 → 可以继续寻找；仍无 → NO_POEM_DIRECTION（合法出口，不编故事）
```

- **不是 Gate**：无 PASS／FAIL，不参与通过／不通过判定，不产生阻断；产物是写作方向，不是检查表。
- 顺序不可跳：裸题（如「凌晨便利店」）必须先形成 Premise 与情感方向，**不得**直接「找四个景物 → 拼成诗句」。
- 已有强情境时（如「祖父去世后第一次回老家，葡萄架还在，没人坐在下面乘凉」）：`PREMISE_FORMATION = SKIP`，
  直接进行 AFFECTIVE INTENT。方向可能自然落在怀念／物是人非，但**不得要求**诗中出现「悲」「思念」「物是人非」。
- `AFFECTIVE_TEMPLATE_GUARD`：夜晚 ≠ 自动孤独、下雨 ≠ 自动惆怅、秋天 ≠ 自动悲凉、故乡 ≠ 自动思乡、
  老人 ≠ 自动怀念、死亡 ≠ 自动哭诉；思想感情只能从「具体处境＋实际关系＋事实变化」自然产生。
  这是 `premise_formation.md` 的 `EMOTION_TEMPLATE_GUARD` 在情感方向阶段的同族约束。
- `FORCED_SIGNIFICANCE_GUARD` 对本步同样生效：不得为了「必须有思想感情」添补输入不支持的重大事实
  （多年未归／父母去世／分手／疾病／人生遗憾／童年伤痛／身份焦虑）。
- 情感可复合、可很轻；「思想」不等于强行上价值（人生哲理／社会寓言／命运思考／时间宏论）。
- 本节点不改变后续步骤编号；跳过或情感很轻时，流水线行为与 v0.1-beta 一致。
- 边界：本步只负责 AFFECTIVE FORMATION，不宣称解决 COMPOSER REALISATION（方向正确仍可能写出生硬句）。

### 主体步骤

> AFFECTIVE INTENT 全程约束（步骤 2-5）：FACT／DISCOVERY／RELATION／CONCEPT
> **优先选择能够承载当前写作方向的事实与关系**；具体但与情感无关的事实可以舍弃。
> 反向禁止：不得为了迎合情感方向歪曲事实或增补事实。

1. 解析题面；注入 Persona 声音/视角（如无 Persona，用中性视角）。
2. COMPOSE·FACT：列可验证事实清单。
3. COMPOSE·IRREPLACEABLE_FACT：三问定位不可替换事实（找不到→回 2 或换题）。
4. COMPOSE·DISCOVERY：产 3 个真不同发现。
5. COMPOSE·CONCEPTS：选 2-3 个完整构思 → 定 1 个主构思。
6. COMPOSE·DRAFT：按语言纪律成稿（可出 1-2 个候选）。
7. CRITIQUE：按批评协议过六项优先检查 + 补查；记录问题到句，并显式落三档判决之一（见下「Critic Runtime Loading」）。
8. REVISE：按修改协议修（每处记录 POETIC_EYE / NATURAL_SYNTAX 两字段）。
9. 调用 chinese-poetry-prosody 验律（PASS/WARN/FAIL + 退出码；按报告行事，不自行判韵）。
10. 修律：只动违规处，≤5 轮，复检至 PASS 或如实报告冲突。
11. FINAL AESTHETIC CHECK：修律后重过一遍 critique 六项（防"律过意伤"）→ 输出最终诗。

## Critic Runtime Loading（按档位取用，不整包加载）

资产在 `references/runtime_teaching/`；DEFAULT AVAILABLE ≠ LOAD EVERYTHING。

- MINIMAL（普通批评、交付前自查）：当前 critique protocol + 最相关的 1 个 contrast。
- STANDARD（已有明确怀疑方向）：1-2 个相关 contrast；**仅**当怀疑打油感／散文压缩时才读 critic_acoustics.md。
- DEEP（疑难、多轮不收敛、需历史近似案例校准）：允许检索 failure_index_retrieval.md + 多个 contrast。
- `failure_index_retrieval.md` 是 CASE RETRIEVAL INDEX：先有具体怀疑，再检索近似案例；
  **不得**逐项扫描 11 类，也不得整包注入 Recovery 材料。

## 未接入（保持实验态）

- `COMPOSER_TEACHING = EXPERIMENTAL_NOT_RUNTIME`；`REVISER_TEACHING = EXPERIMENTAL_NOT_RUNTIME`。
- 研究仓的 teaching 单元不由本 Skill 自动读取；Orchestrator 不得因为文件存在就注入轨迹教学。
- 既有已验证／历史支持的原则继续有效：`POETIC_EYE_PRESERVED`；修律可撤回（prosody repair may be rolled back）。
  这不等于 trajectory injection 已验证。

## 循环与上限

- compose 构思轮数 ≤3（第 8 节上限）；仍无自然稿 → UNRESOLVED，如实报告。
- critique → revise 循环 ≤3 轮；不收敛 → 按 revise 分层回退（换 CONCEPT），不在语言层死磨。
- 修律轮 ≤5；冲突 → 保诗眼，冲突项交用户。
- 任一步失败都不静默降级：报告层位（构思/关系/语言/格律）与已试方案。

## 输出纪律

- 默认只展示：最终诗 + 极简必要说明（题目/体裁/一句注记，按需）。
- 内部分析（FACT 清单、DISCOVERY 过程、CRITIQUE 记录、修律版本）默认不展示；用户要求时再展开。
- 保留中间版本痕迹（修订记录在内部，交付内容干净）。

## 用户偏好层（Soft Preference Profile）

- 默认 OFF：本 Skill 面向通用使用，不把任何单一用户的偏好当规则。
- 当前内置软偏好来自一位用户的真人评审（15 组/16 首认可，见 references/user_soft_preferences.md），
  仅当调用方为该用户或明示"按其偏好创作/评审"时开启。
- 开启后仍受 compose/critique 反伪规则约束（不得模板化：短句/对称/无「的」/动态/口语都不是硬门槛）。

## 验律调用契约（示例，实际以 prosody 文档为准）

外部命令（在 chinese-poetry-prosody 根目录执行）：
py scripts/check_poem.py --poem "<诗>" --form jueju5|jueju7 [--reading 字=拼音|行:列=拼音] [--rhyme-profile xinyun18]
判定：PASS=0 / WARN=1 / FAIL=2；WARN 是提示不是硬伤，FAIL 必须修。
本 Skill 不复制、不解释其内部韵书逻辑；多音字等歧义以 --reading 如实锁定，不猜测。
