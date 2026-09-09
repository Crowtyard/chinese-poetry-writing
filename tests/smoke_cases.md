# tests/smoke_cases.md —— v0.1-beta 冒烟用例（STEP 4B 定稿题目）

用途：验证 Skill 端到端可用（COMPOSE→CRITIQUE→REVISE→PROSODY→FINAL CHECK），不做大规模 A/B。
执行与记录：tests/smoke_results.md。每题检查：DISCOVERY_VARIETY / IRREPLACEABLE_FACT_PRESENT /
RELATION_PRESENT / NATURAL_LANGUAGE / EXPLANATION_AFTER_DISCOVERY / FORCED_SYMBOLISM /
DE_OVERUSE / STYLE_COLLAPSE / PROSODY_CALLED / POETIC_EYE_PRESERVED_AFTER_PROSODY。

## 用例（用户指定，题材覆盖 现代/古典自然/离别/日常/人物/城市）

| ID | 题目/场景 | 覆盖 |
|---|---|---|
| S01 | 高铁离乡 | 现代/离别 |
| S02 | 山雨 | 古典自然 |
| S03 | 久别重逢 | 人物/离别 |
| S04 | 深夜办公室 | 现代/日常 |
| S05 | 医院走廊 | 现代/城市 |
| S06 | 秋江 | 古典自然 |
| S07 | 旧物 | 日常/人物 |
| S08 | 家庭等待 | 日常/家庭 |
| S09 | 古典山水 | 古典自然 |
| S10 | 自由题（鱼市收摊） | 现代/城市/日常 |

## 执行要求

- 每题走完整 ORCHESTRATE 流程；记录诗眼与关系类型，防止共用同一模板。
- prosody 调用失败 → 该例记 FAIL，不得伪造。
- 验收：SMOKE_TESTS_PASS = n/10；出现同模板反复/修律持续伤诗眼/Critic 大量误杀/工作流无法完成 → READY_FOR_USER_BETA = FALSE。
