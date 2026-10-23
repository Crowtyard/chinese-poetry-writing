---
name: chinese-poetry-writing
description: 中文诗歌创作、批评、修订与原文查询 Skill。可按作者、标题、正文关键词、文集或词牌检索本地 chinese-poetry 原文库，带来源参考古人写法与比较风格；适用于写诗、填词、改诗、点评、查诗、找名句、查作者。纯声韵与格律问题交给 chinese-poetry-prosody。
metadata:
  version: "0.4-beta"
---

# chinese-poetry-writing —— 中文诗歌创作、查询与修订 Skill（v0.4-beta）

## 名称与版本

- skill_name: chinese-poetry-writing
- version: v0.4-beta
- 性质：BETA。提供已验证的方法，不宣称审美模型已经客观完备。
- 集成状态：保留 v0.1-beta 的 MINIMUM_PRODUCT_INTEGRATION_V1 + AFFECTIVE_INTENT_FLOW_V1（运行时教学资产已接入
  `references/runtime_teaching/`，接入范围与档位见「Runtime Teaching」一节；主流程新增
  AFFECTIVE INTENT 写作准备步骤，见「AFFECTIVE INTENT（思想感情方向）」一节）。
- v0.2 新增：创作前选择体裁、韵书、词谱变体；接入姊妹项目的可选传统查询与词稿复核。
  未新增传统整诗合律认证，详见 `references/prosody_selection.md`。
- v0.3 新增：参考 ALDIFS/Poetry-meter-skill，加入关键细节保留、语体组织、炼字、
  视点与虚实核对、按需用典和朗读推敲；详见 `references/craft_revision.md`。
  这些是待真人验证的参考方法，不是新增真人教学资产；来源及取舍见 `references/sources.md`。
- v0.4 新增：参考 Wscats/poetry-skills 的本地 JSON 联动，接入独立 chinese-poetry 原文库，
  提供可执行的查询、简繁匹配、作者资料及来源追溯，详见 `references/corpus_retrieval.md`。

## 职责（COMPOSE / CRITIQUE / REVISE / ORCHESTRATE）

- COMPOSE：如何发现诗眼、如何构思、如何成稿。
- CRITIQUE：如何批评诗稿（自查与他评共用同一纪律）。
- REVISE：如何修改（先保什么、后动什么、何时回退）。
- ORCHESTRATE：全流程调度、迭代上限、输出纪律。
- QUERY：检索原作、作者资料和用例；为需要参考原作的创作提供可追溯材料，不代替验律。

本 Skill 不绑定任何具体 Persona。小光、Kun 及其他角色均可调用。

## 职责边界

| 层 | 负责 |
|---|---|
| Persona（角色） | 人格、经历、视角、声音（永不并入本 Skill） |
| Writing Skill（本文件） | 写诗的方法：发现→构思→成稿→批→改 |
| chinese-poetry-prosody | 确定性验律（拼音/平仄/押韵/相对/相粘/韵部），独立存在 |

## 触发条件

用户要求以下任一时可加载本 Skill：
写诗、作诗、填词、写五绝、写七绝、写古诗、写格律诗、命题诗、润色诗、改诗、批评/点评诗稿、
查诗、按作者/标题/词牌找诗、查名句或典故用例、比较诗人表达，以及完整创作工作流。

以下情况**不**进入创作流程，优先转交 chinese-poetry-prosody：
仅查询押韵、查平仄、查韵部、验某诗是否合律、多音字读音——由 chinese-poetry-prosody 处理。

## 调度流程（ORCHESTRATE）

先区分意图：纯查诗/查作者走 QUERY；纯声韵查询走 prosody；创作、点评、修订走原流程。
用户要求参考古人、风格比较、典故用例或核对出处时，先按需读 `references/corpus_retrieval.md`，
执行实际查询再分析。普通创作不强制查库，不将整个数据库加载进上下文。

```
USER_REQUEST
↓
INTENT → 纯查询：检索原库 → 带来源回答（不进入创作/验律）
       → 创作/改诗：需要原作参考时先查询少量相关作品
↓
FORM / RHYME SYSTEM（先明确体裁、韵书；填词先查词谱和确切变体）
↓
PREMISE STATUS CHECK（条件式，非必经 Gate；细则见 protocols/orchestration.md 步骤 0）
  输入已含具体处境／关系／stake → 继续（跳过 Formation）
  否则 → 轻量初始 Discovery 探针
    Discovery 已带 stake → 继续
    仍是纯观察 → PREMISE_FORMATION（references/runtime_teaching/premise_formation.md）
    找不到自然 Premise → NO_POEM_DIRECTION（合法出口，不编故事）
↓
AFFECTIVE INTENT（思想感情方向；写作准备步骤，非 Gate；细则见下节与 orchestration 步骤 0.5）
  这个处境里真正牵动人的是什么 / 本诗准备承载什么思想感情 / 哪些事实物象能承载它
  自然形成 → 继续；情感很轻 → 同样合法；找不到自然方向 → 继续寻找或 NO_POEM_DIRECTION（不硬贴模板）
↓
COMPOSE（FACT / DISCOVERY / RELATION / CONCEPT 均受 AFFECTIVE INTENT 约束）
  FACT
  IRREPLACEABLE_FACT
  DISCOVERY（≥3）
  RELATION
  CONCEPTS（2-3）
  DRAFT
  核对关键关系与细节；朗读；按需要推敲语体、词语、布局或用典
↓
CRITIQUE（EVIDENCE / RELATION / NATURALNESS / EXPLANATION /
         TECHNIQUE_VISIBILITY / IRREPLACEABILITY）
↓
REVISE
↓
调用 chinese-poetry-prosody 对应入口（现代绝句检查 / 传统资料与词稿外部复核 / 自由诗不套绝句）
↓
现代检查有确定违规 → 修订并复检；传统外部提示 → 先核对资料，不直接判必改
↓
FINAL_AESTHETIC_CHECK（修律后重过 CRITIQUE 核心项）
↓
OUTPUT
```

- 内部分析（FACT/DISCOVERY/CRITIQUE 过程）默认不展示给用户；仅输出诗与必要说明。
- 迭代上限：构思 ≤3 轮；批评-修订 ≤3 轮；修律 ≤5 轮。不收敛则如实报告 UNRESOLVED。

## 原文查询与参考（v0.4）

- 首次准备：在本仓库根目录运行 `python3 scripts/setup_poetry_library.py`；原库与索引放在仓库之外，
  固定版本、保留 LICENSE；刷新与路径参数见 `references/corpus_retrieval.md`。
- 查询示例：`python3 scripts/poetry_library.py --json search --author 李白 --keyword 明月 --limit 3`。
  宋词用 `--rhythmic` 查词牌，不把词牌当独立题名；支持简繁匹配，展示保留原文。
- 引用实际返回的作者、标题/词牌、完整正文及来源；不捏造结果、把本页当全部，或把字面关键词当语义标签。
- 创作时只借鉴适合本次处境的句法、布局与关系方法，核对用典，不照搬原句或原作事件。
- 原库、注释及其 `strains` 不替代韵书/词谱，库内命中不是格律认证或审美背书。
  软件测试也不证明新创作质量更好。查询未完成时说明，不靠记忆冒充查库。

## 成稿与推敲（v0.3）

- 起草前用一行内部记录保留重要人物、动作方向、时间/醒梦边界及两三项关键细节；不要求穷尽事实。
- 起草后核对这些内容是否仍可读出，并朗读整句；需要修词、布景或用典时按需取
  `references/craft_revision.md` 对应小节。保持现有 Critic 六项与三档判决，不增设评分或 Gate。
- 传统语体可凝练，现代题材可保留现代词；不把“像古诗”作为删去经历特征的理由。
- 用典先核对本义、出处与当前关系；普通朋友不自动写成生死知音，不能把梦中来信变成现实来信。
- 修词与修律后再核对关键语义。听觉自查不代替程序验律，形式 PASS 不抵消素材丢失。

## AFFECTIVE INTENT（思想感情方向 / AFFECTIVE_INTENT_FLOW_V1）

位置：PREMISE STATUS CHECK 之后、COMPOSE 之前。执行细则见 `protocols/orchestration.md` 步骤 0.5；
写作层约束见 `protocols/compose.md`；Critic 侧只多问一个问题（见 `protocols/critique.md`）。

它补的是 Premise 没有回答的那一层：
`Premise: 为什么这件事值得写？` → `Affective Intent: 这个具体处境里真正牵动人的是什么？这首诗准备承载什么思想感情？`

只回答三个问题（运行时内部完成，默认不展示给用户；不扩展成 10/20 条 checklist）：

```text
1. 这个具体题材／处境中，真正触动人的是什么？
2. 从这个处境自然生长出来的主要思想感情是什么？
3. 哪些事实、动作、关系、物象能够承载这种感情，而不必把感情直接解释出来？
```

- **不是 Gate**：无 PASS／FAIL，不参与通过／不通过判定，不产生阻断；产物是一句内部写作方向。
- 产物必须真正约束后续：FACT／DISCOVERY／RELATION／CONCEPT **优先选择能够承载当前方向的
  事实与关系**；具体但与情感无关的事实**可以舍弃**（要修的正是「事实具体，但没有情感必要性」）。

核心纪律：

1. `AFFECTIVE_INTENT != EMOTION_WORDS` —— 先明确思想感情，不等于把悲伤／孤独／思念／惆怅／
   人生／命运／岁月／成长这些词直接塞进诗里。情感应影响的是 WHAT TO NOTICE / WHAT TO SELECT /
   WHAT TO OMIT / HOW RELATIONS ARE ORGANISED / WHERE THE POEM STOPS。
2. 感情藏在诗里：优先通过人与物的关系、人与人的关系、现在与过去的差异、动作未完成、
   熟悉之物与缺席之人的反差、物象变化、语气、节奏、留白、结尾位置让它出现。
   思想感情是内部写作方向，**不要求**作为抽象词直接出现在诗中。
   目标：`READER_FEELS_IT_BEFORE_THE_POEM_EXPLAINS_IT`。
3. 情感不是单标签：允许「怀念＋悲戚」「亲昵＋怅惘」「喜悦＋不舍」「安静＋满足」「荒诞＋讽刺」这类复合，
   但**不强制**双情绪；只需准确描述当前诗真正要承载的感受或认识。**克制不等于没有感情。**
4. 「思想」不等于强行上价值：对关系的认识、某一刻突然意识到什么、对变化的体会、
   对人的处境的理解都算；不得默认升级成人生哲理／社会寓言／命运思考／时间宏论。
5. `AFFECTIVE_TEMPLATE_GUARD`（禁止机械映射）：夜晚 ≠ 自动孤独；下雨 ≠ 自动惆怅；秋天 ≠ 自动悲凉；
   故乡 ≠ 自动思乡；老人 ≠ 自动怀念；死亡 ≠ 自动哭诉。
   思想感情必须从「具体处境 ＋ 实际关系 ＋ 事实变化」自然产生。
   （与 `references/runtime_teaching/premise_formation.md` 的 `EMOTION_TEMPLATE_GUARD` 同族：
   那条约束 Premise 阶段，本条约束情感方向阶段。）
6. `FORCED_SIGNIFICANCE_GUARD` 继续有效，并同样适用于本步：题材本身情感弱时，**不得**为了
   「必须有思想感情」强造多年未归／父母去世／分手／疾病／人生遗憾／童年伤痛／身份焦虑等
   输入并不支持的事实。允许情感很轻，也允许 `NO_POEM_DIRECTION`（合法出口，不编故事）。

边界：本步只解决 AFFECTIVE FORMATION，**不**宣称已解决 COMPOSER REALISATION——
方向正确仍可能写成生硬句，那属于语言实现问题，不由本步负责。

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

- 先按 `references/prosody_selection.md` 选择体系；采用用户指定条件，不为通过检查暗换韵书。
- 完成审美稿后调用 `chinese-poetry-prosody` 的实际检出/安装路径，不假定个人目录存在。
- 现代五绝/七绝在姊妹仓库根目录执行：
  `python3 scripts/check_poem.py --poem "<诗>" [--form jueju5|jueju7] [--reading 行:列=拼音] [--rhyme-profile xinyun18]`。
  未指定韵书的绝句保留现代十八韵默认，并注明“现代普通话简化规则”。
- 传统查韵、查词谱、词稿外部匹配调用 `traditional_prosody.py`；填词先查询确切词牌与变体。
  外部匹配始终 WARN / EXTERNAL_REVIEW_REQUIRED，不提供传统整诗 PASS。缺后端或资料时说明未完成验律。
- 自由诗不运行绝句扫描。古人作品或传统规则请求，不用现代普通话声调代替古音平仄。
- 原生现代判定：PASS 可交付但不代表审美合格；WARN 按提示决定；确定 FAIL 修订后复检。
  传统外部提示须核对字表覆盖、语境读音、词谱变体及典籍后再决定，不自动改古人作品。
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
- references/prosody_selection.md —— 体裁、韵书、词谱变体选择与外部复核边界（v0.2）
- references/craft_revision.md —— 成稿、语体、炼字、布局、用典与朗读（v0.3；按需读取）
- references/sources.md —— 外部参考版本、采用范围与证据边界
- references/corpus_retrieval.md —— 原文库安装、查询、风格参考与引用边界（v0.4）
- scripts/setup_poetry_library.py / poetry_library.py —— 独立数据准备与只读检索工具
