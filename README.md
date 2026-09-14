# Chinese Poetry Writing

> 中文诗歌创作 Skill。把「选材 → 发现 → 成诗 → 批评 → 修订 → 验律」拆成可追踪的流程，
> 并把真人审美反馈与失败案例蒸馏为**运行时校准资产**，而不是一叠写作口诀。

`v0.1-beta`｜`REAL_USER_BETA`｜main 已集成 Minimum Product Integration V1（条件式 Premise Formation + 带证据门槛的 Critic 运行时校准）

它**不是**「一个万能写诗 Prompt」。

## 为什么做这个

普通 AI 写诗常见的问题，基本都落在同一个地方：

- **画面有，但只是记录** —— 事实摆齐了，却没有东西推动它们的排列；
- **把「具体事实」误当成「诗」** —— 细节很具体，但事实之间不发生关系；
- **为押韵压坏正常汉语** —— 韵脚挑词，句子先塌；
- **抽象情绪直接贴上去** —— 悲伤、孤独、思念写在纸上，读者只收到标签；
- **Critic 见什么都想改** —— 把不构成失败的风险写成必改项；
- **把格律 PASS 误当成「诗写得好」** —— 形式过关被当成审美合格。

这个项目就是围绕这些失败类型建的：先把诗写成立，再把律验通过，两者不互相冒充。

## 核心原则

- **具体事实 ≠ 诗。** 物证在场只是入场券；核心要有互相定义的关系（≥2 级）或一条动作-反应链。
- **`Prosody PASS` ≠ 审美合格。** 验律是确定性判定，审美判断独立于它。
- **Critic is a diagnostician, not an aesthetic sovereign.** 批评者只诊断文本在做什么，不替作者立审美法。
- **`LOCAL_RISK != POEM_FAILURE`。** 登记一处可指认的风险，不等于判作品失败。
- **先写成诗，再验成律；律为诗服务，不让律替诗活。** 修改优先级固定为：诗眼 → 关系 → 不可替换事实 → 自然语言 → 格律，低层改动不得损伤高层。
- **程序负责确定事实，LLM 负责诗意判断。** 拼音、平仄、押韵、韵部一律由脚本判定，模型不猜。
- **规则必须知道自己的边界。** 每条从真人证据里提炼的经验，入库时同时登记它「不可推广成什么」。

## 架构：三层职责分离

```text
Persona（谁在写）
   ↓  人格 / 经历 / 视角 / 声音
chinese-poetry-writing（本仓库）
   ↓  发现 / 构思 / 成诗 / 批评 / 修订 / 调度
chinese-poetry-prosody（独立项目·确定性验律）
      拼音 / 平仄 / 押韵 / 相对 / 相粘 / 韵部
```

- **Persona**：谁在写。本 Skill 不绑定任何 Persona，也不把人设并进方法层。
- **chinese-poetry-writing**：怎么写、怎么批、怎么改、怎么调度。
- **chinese-poetry-prosody**：唯一验律方。本仓库**不**内嵌拼音表与韵书数据，也不复制其判定逻辑；成稿后调用它、按报告修律、修完复检。

## 当前工作流（v0.1-beta）

```text
INPUT
 ↓
PREMISE STATUS CHECK ← 条件式，非必经节点
 ├ 输入已含具体处境 / 关系 / stake → 跳过 Premise Formation
 └ 裸题 → 轻量初始 Discovery 探针
      ├ Discovery 自身已带 stake → 跳过
      ├ 仍是纯现象 / 纯观察 → PREMISE_FORMATION（条件式）
      └ 找不到自然 Premise → NO_POEM_DIRECTION（合法出口：如实报告，不编故事）
 ↓
FACT → IRREPLACEABLE_FACT → DISCOVERY(≥3) → RELATION → CONCEPT(2-3) → DRAFT
 ↓
CRITIQUE（EVIDENCE / RELATION / NATURALNESS / EXPLANATION / TECHNIQUE_VISIBILITY / IRREPLACEABILITY）
 ↓
REVISE（每处改动记录 POETIC_EYE_PRESERVED / NATURAL_SYNTAX_PRESERVED）
 ↓
PROSODY（调用 chinese-poetry-prosody：PASS / WARN / FAIL）
 ↓
修律 → 复检（只动违规处，最多 5 轮）
 ↓
FINAL AESTHETIC CHECK（修律后重过 critique 核心项，防「律过意伤」）
 ↓
OUTPUT（默认只交付诗 + 极简说明）
```

- `PREMISE_GATE = OPTIONAL_DIAGNOSTIC`：只用于「Discovery 很聪明，但说不清为什么值得写」的疑难情况；它**不是**必经关卡，不参与通过／不通过判定。
- 迭代上限：构思 ≤3 轮，批评-修订 ≤3 轮，修律 ≤5 轮；不收敛就如实报告 `UNRESOLVED`，不静默降级。

## 与普通 AI 写诗 Prompt 的差别

**条件式 Premise Formation。** 只在「裸题 + 初始 Discovery 仍是纯观察」时启动：去找一个**已经存在于事实可能性中**的处境／关系／变化，让后续选材有方向。它不生产新事实，只改变「看什么」（ATTENTION_SHIFT）；输入自带处境或 Discovery 本身已带 stake 时跳过。已知边界：`PREMISE_FORMATION_UNIVERSALLY_BETTER = NO` —— 历史盲评里它也输给过直接 Discovery（PF 6 胜 / Direct 1 胜 / 平 2），所以这是一条条件式支路，不是万能步骤。

**带证据门槛的运行时校准（Evidence-gated runtime teaching）。** 研究资产不整包进运行时。只有满足证据门槛（真人裁决 + 可追溯来源 + 明确「不可推广」边界）的内容，才被蒸馏进 `references/runtime_teaching/`。其中 `failure_index_retrieval.md` 是**案例检索索引**：先有具体怀疑，再去检索近似案例，不逐项扫描、不作为通过／不通过的判据。

**对照式 Critic 校准（Contrastive calibration）。** 调用 Critic 不等于必须找出问题，三档判决都合法：

| 判决 | 含义 |
|---|---|
| `MATERIAL_PROBLEM` | 有足以要求修改的实质问题（必须落到句 + 根因 + 修改方向） |
| `LOCAL_RISK` | 有可指认的风险，但不足以判作品失败（只登记，不强制修改） |
| `NO_MATERIAL_PROBLEM` | 无实质问题（必须说明**为什么成立**、它做了什么工作） |

校准资产的形式是成对的对照：同一条表面风险，为什么在此处成立、在彼处不成立。协议同时明令禁止「为了显得尽责而制造问题」，以及给已判无实质问题的文本追加「可以更凝练／更雅／更生动」式装饰建议。

**过度解释护栏（Interpretive Overreach Guard）。** 原则是 `DIAGNOSE WHAT THE TEXT DOES`：Critic 可以解释诗中已有的语言关系如何工作，但不得把可能的心理故事、隐藏主题或象征意义说成作者已经确定表达的意思。例如一首重逢诗里「早认 → 方观 → 未唤名」的递进可以被指出；而「先认出时间没改掉的部分，再确认时间改掉的部分」这类替诗补出来的意义会被拦下（真人判定：替诗补了一层解释）。

**可追溯性（Traceability）。** 每个运行时资产都保留五个字段：`SOURCE_CASE`、`SOURCE_EVIDENCE`、`HUMAN_VERDICT`、`WHAT_WAS_PRESERVED`、`WHAT_WAS_NOT_GENERALIZED`。目的很实际：防止以后把真实案例错误压缩成一句僵硬规则 —— 每条经验都要带着「它不许被推广成什么」一起入库。

## 运行时教学档位

`DEFAULT AVAILABLE != LOAD EVERYTHING`：资产默认可用，但不等于默认整包加载。

| 档位 | 何时 | 加载 |
|---|---|---|
| MINIMAL | 普通批评、交付前自查 | 批评协议 + 最相关的 1 条对照 |
| STANDARD | 已有明确怀疑方向 | 1–2 条相关对照；仅怀疑打油感／散文压缩时才加声学诊断 |
| DEEP | 疑难、多轮不收敛、需历史近似案例校准 | 允许检索 failure index + 多条对照 |

档位只决定「取多少材料」，不改变判决标准，也不代表质量保证。

## 快速开始

直接下指令即可（题目、体裁、要求都写在自然语言里）：

```text
写一首关于「凌晨便利店」的诗。

把这首诗改成五绝，并说明你删掉了什么、为什么。

点评这首诗：它最实质的问题是哪一句？（允许回答「没有实质问题」）
```

- **只想验律**（查押韵、平仄、韵部、某诗是否合律）→ 直接交给 chinese-poetry-prosody，不进入创作流程。
- 内部分析（FACT 清单、DISCOVERY 过程、批评记录、修律中间版本）默认**不**展示，只交付诗与必要说明；需要时明确要求展开。
- 安装：本仓库本身就是 Skill 目录，把它放进你所用的客户端 Skill 路径即可（Codex 个人级 Skill 目录形如 `$HOME/.agents/skills/<skill-name>/`）。仓库内 `agents/openai.yaml` 提供客户端展示名与默认提示。本仓库没有自动安装脚本，也没有发布到任何技能市场。

## 姊妹项目：chinese-poetry-prosody

<https://github.com/Crowtyard/chinese-poetry-prosody>

- **确定性**：拼音、声调、平仄、现代韵（中华新韵十八韵／十四韵、十三辙、听感近韵）、联内相对、联间相粘、韵脚与整诗扫描，全部由数据 + 程序计算。
- 以**现代普通话**为准，不是历史音韵学系统。
- 报告 `PASS` / `WARN` / `FAIL`，退出码 `0` / `1` / `2`；`WARN` 是提示，`FAIL` 必须修改对应句后复检。
- **它只判格律，不做审美判断**：验律通过不代表诗成立。

```bash
# 在 chinese-poetry-prosody 仓库根目录执行（用法以其 README / SKILL.md 为准）
py scripts/check_poem.py --poem "<诗>" --form jueju7 [--reading 行:列=拼音] [--rhyme-profile xinyun18]
```

## 项目结构

```text
chinese-poetry-writing/
├── SKILL.md              # Skill 定义：职责边界、触发条件、调度流程、教学档位、Prosody 集成契约
├── protocols/            # 执行细则
│   ├── orchestration.md  # 流水线编排：条件式 Premise 检查、11 步主体、循环上限、输出纪律
│   ├── compose.md        # 创作：FACT → … → DRAFT 的发现纪律与语言纪律
│   ├── critique.md       # 批评：六项优先检查、三档判决、过度解释护栏
│   └── revise.md         # 修订：诗眼优先的改动优先级与修律纪律
├── references/           # 判据速查（发现 / 关系 / 留白 / 结尾 / 坏诗模式 / 软偏好层）
│   └── runtime_teaching/ # 通过证据门槛的运行时校准资产（critic 对照・声学诊断・案例索引・Premise Formation）
├── examples/             # 真人裁决样本（获认可 / 失败），可学不可抄
└── tests/                # 冒烟用例清单（v0.1-beta 验收）
```

## 证据与真人反馈

这个项目的扩张顺序不是「先写一套好诗规则，再让模型遵守」，而是：

```text
生成 → 真人反馈 → 诊断失败原因 → 修改 → 推翻错误结论
     → 保留成功案例 → 形成对照 → 通过证据门槛后进入运行时
```

- **真人裁决优先于模型自证**：一个机制只有被隔离验证过才写进协议；被真人否掉但确实动人的反例会被保留，用来限定规则边界。
- 这里**没有**权重训练、fine-tuning、RLHF —— 全部校准都发生在 Skill／提示运行时层面，可审查、可回滚。
- 项目在真实用户 Beta 中暴露过「具体事实过拟合」「打油诗式压缩」「Critic 过度解释」等失败类型，并据此修订了协议与资产。

## 已知边界

- 格律正确不代表诗好：`Prosody PASS` 只是形式事实。
- **Composer 的实现（realisation）仍是开放问题**：方向对、句子仍可能写生硬。
- Composer／Reviser 的对照教学仍是**实验态**，稳定运行时不加载：
  `COMPOSER_TEACHING = EXPERIMENTAL_NOT_RUNTIME`、`REVISER_TEACHING = EXPERIMENTAL_NOT_RUNTIME`。
- 运行时校准是**方向性**的：它减少明显误判，不构成审美可靠性的证明。
- Critic 有误杀也有放过（FP／FN 都存在），所以协议保留 `NEEDS_HUMAN` 出口，宁可留白也不硬判。
- 用户软偏好层默认**关闭**：默认通用模式，不把任何单一用户的偏好当规则。

## 版本与状态

- version：`v0.1-beta`
- status：`REAL_USER_BETA`
- main：已集成 Minimum Product Integration V1 —— 条件式 Premise Formation + 带证据门槛的 Critic 运行时校准
- 验收：`tests/smoke_cases.md` 共 10 题冒烟用例，走完整端到端流程（COMPOSE → CRITIQUE → REVISE → PROSODY → FINAL CHECK），题材覆盖现代／古典自然／离别／日常／人物／城市
- Beta 的含义：提供已验证的方法，**不**宣称审美模型已经客观完备。
