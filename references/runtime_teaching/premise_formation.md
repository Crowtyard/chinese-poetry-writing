# references/runtime_teaching/premise_formation.md —— Premise Formation（条件式运行时压缩资产）

> RUNTIME_ASSET · MINIMUM_PRODUCT_INTEGRATION_V1 ｜ TIER = RUNTIME_CONDITIONAL（仅裸题触发，非必经步骤）
> SOURCE_CASE = recovery/teaching/premise_formation_experiment_v1.md（RUN1）/ _v1_r2.md（RUN2）/ _v1_r3.md（RUN3）；九题概念对原文见 premise_formation_human_freeze_v1.md
> SOURCE_EVIDENCE = 模型侧 9 题 ATTENTION_SHIFT = YES、PREMISE_POST_HOC = NO（三轮）；真人盲评 9/9 裁决完成；三轮共 9 个候选 Premise 被 REJECT（不可现场验证／需编造具体人／与既有 Discovery 同源的事后解释）
> HUMAN_VERDICT = PF 6 胜 / Direct 1 胜 / Tie 2 / BOTH_WEAK 0（HUMAN_GATE = PARTIAL_POSITIVE）
> WHAT_WAS_PRESERVED = 条件触发；事实支持优先于故事；NO_NATURAL_PREMISE_FOUND 合法；三个 Guard
> WHAT_WAS_NOT_GENERALIZED = `PREMISE_FORMATION_UNIVERSALLY_BETTER = NO`；`WIN_CAUSE = UNKNOWN`（无盲态 ONE_REASON，不得宣称胜因必然来自 Premise-level value）；Direct 的 TIE ×2 与 WIN ×1（夜市收摊）必须保留
> 溯源指针：SOURCE_* 只用于追溯证据来源（研究仓原文），**不是**运行时依赖；运行时只读本目录与 protocols/。

## 它是什么 / 不是什么

- 是：从裸题里找出一个**已经存在于事实可能性中的**处境、关系、变化、认识或感知压力，
  使后续 FACT SEARCH 有方向。
- 不是：加感情、加故事、加设定、加主题。
  Premise Formation 不生产新事实，它只改变「看什么」（ATTENTION_SHIFT）。

## 触发条件（条件式）

```text
输入已含具体处境／关系／stake／meaningful tension → SKIP
裸题 + 初始 Discovery 仍是纯现象、纯观察        → FORMATION
裸题，但 Discovery 自身已带 stake               → MAY_SKIP（不得为「做人化」强行替换已有的好 Discovery）
FORMATION 找不到自然 Premise                     → NO_NATURAL_PREMISE_FOUND → NO_POEM_DIRECTION（合法出口）
```

## 三问启发（候选 Premise 的验收）

带 2-3 个候选（候选之间必须真的不同，不是同一处境的措辞变体），逐个问：

1. **事实支持吗？** 能否立刻指出支持它的事实？不能 → REJECT。
2. **它改变了「看什么」吗？** 若只是换一套说法描述同一个 Discovery → 不是 Premise，回退。
   （与现有 Discovery 同源的候选 = 事后解释，REJECT。）
3. **它能让 FACT SEARCH 有方向吗？** 后续能列出的事实是否围绕这个处境／关系聚集？

纪律：

- 先有候选，再看是否成立；不得先写成诗再补一个 Premise 去解释它（PREMISE_POST_HOC = NO）。
- 故事性强的候选先按第 1 问筛（历史样本中编造型候选全部 REJECT，未为完成任务补剧情）。

## 合法出口

`NO_NATURAL_PREMISE_FOUND` 是合法结论：如实报告「这个题目当前没有找到值得写的处境」，
输出 `NO_POEM_DIRECTION`，不写诗。**不得**为了完成写诗任务强造处境或补剧情。

## Guards

### STORY_INVENTION_GUARD

不得为了形成 Premise 虚构具体人物、具体事件、具体经历
（某位熟客的固定口味、某摊主与家人视频、一段未交代的往事……）。
Premise 只能来自题目自身可列出的事实。

### EMOTION_TEMPLATE_GUARD

不得把题目套进现成情绪模板。尤其禁止为了形成 Premise 自动注入：
死亡／分手／多年未归／疾病／孤独／人生／命运／成长／时间流逝。
这些**只有事实本身支持时才可出现**。

### FORCED_SIGNIFICANCE_GUARD

不得为了「让题目显得值得写」强行拔高或追加重量（历史记录中一次「灯的忠诚」式措辞在 Guard 下被否决）。
找不到有分量的事实就是找不到 → 回 `NO_POEM_DIRECTION`，而不是加一句意义。

## Premise Gate（OPTIONAL_DIAGNOSTIC）

`PREMISE_GATE` 不是必经节点：不参与通过／不通过判定，不产生阻断，不得替代 Discovery。
只在疑难情况使用：「这个 Discovery 很聪明，但为什么值得写说不清楚」。

其历史形态的三问：WHY THIS?（换成相邻题材是否仍成立）／STAKE（注意中心是否被改变）／
POEM NOT NOTE?（是否一句话就说完了）。

历史消融结果：前提已存在时 Gate 的边际效应 = REDUNDANT_SIGNAL（选择未变，被淘汰的候选本来也不会起草）。

## 与 Direct Discovery 的关系

- Formation 不是 universal improvement：真人盲评 9 题中 Direct 有 2 次 TIE、1 次胜出。
- 因此 **Formation 产物不得自动否决已带 stake 的 Direct Discovery**。
- 监控项（仅登记，不据此判优）：Formation 产物存在向既有成功机制家族（如「逐层显现／依次熄灭」）靠拢的倾向。
