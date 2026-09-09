# protocols/orchestration.md —— 编排协议（v0.1-beta / STEP 2）

把 compose / critique / revise / 外部 prosody 串成一条可执行流水线，并规定循环上限与角色边界。

## 角色边界

- Persona / LLM 调用方：人格、经历、视角、声音；提供题目或素材。永不并入本 Skill。
- chinese-poetry-writing：方法（发现→成稿→自查→修订）。本层不内嵌任何拼音/平仄/韵部数据。
- chinese-poetry-prosody：唯一验律方（外部 CLI，只读判定）。本层只负责成稿后调用、按报告修律、复检。

## 标准工作流（11 步）

1. 解析题面；注入 Persona 声音/视角（如无 Persona，用中性视角）。
2. COMPOSE·FACT：列可验证事实清单。
3. COMPOSE·IRREPLACEABLE_FACT：三问定位不可替换事实（找不到→回 2 或换题）。
4. COMPOSE·DISCOVERY：产 3 个真不同发现。
5. COMPOSE·CONCEPTS：选 2-3 个完整构思 → 定 1 个主构思。
6. COMPOSE·DRAFT：按语言纪律成稿（可出 1-2 个候选）。
7. CRITIQUE：按批评协议过六项优先检查 + 补查；记录问题到句。
8. REVISE：按修改协议修（每处记录 POETIC_EYE / NATURAL_SYNTAX 两字段）。
9. 调用 chinese-poetry-prosody 验律（PASS/WARN/FAIL + 退出码；按报告行事，不自行判韵）。
10. 修律：只动违规处，≤5 轮，复检至 PASS 或如实报告冲突。
11. FINAL AESTHETIC CHECK：修律后重过一遍 critique 六项（防"律过意伤"）→ 输出最终诗。

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
