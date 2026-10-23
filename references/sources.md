# 外部学习来源与采用边界

## Wscats/poetry-skills 与 chinese-poetry 原文库

- 参考项目：[Wscats/poetry-skills](https://github.com/Wscats/poetry-skills)，MIT，Copyright (c) 2026 enoyao。
- 阅读版本：`5bcb37e3fe86c9acacbbf914adce3feb921848f8`；阅读了 SKILL.md、PROMPT.md、setup.sh 及 LICENSE。
- 数据来源：[chinese-poetry/chinese-poetry](https://github.com/chinese-poetry/chinese-poetry)，
  固定版本 `b8594f81a89752241442f2ce267d6f66f96704ee`；MIT，Copyright (c) 2016 JackeyGao。
  本地独立原库保留其 LICENSE 与 Git 元数据；索引记录原文件、JSON Pointer、版本、文件哈希与空正文情况。
- 落地：`corpus_retrieval.md`、`scripts/setup_poetry_library.py`、`scripts/poetry_library.py` 与查询路由。
  安装器、适配器、SQL 查询与测试为本项目独立实现，未复制上游程序或提示词全文。
- 简繁检索使用固定版本 `opencc-python-reimplemented==0.1.7` 的 t2s 规则，
  其安装包及许可保留在独立虚拟环境中；仅影响检索字段，不改原作。

### 学到的联动方式及本项目的实现

| Wscats 的做法 | 本项目的落地与调整 |
|---|---|
| 小型 Skill 与大型数据集分开发放，初始化时 Git 下载 | 语料固定版本放在仓库外，重复安装检查来源和状态，不删除 Git 信息或覆盖本地更改 |
| 按文集目录与 JSON 字段定位作品 | 显式选择文集并适配正文格式、章节/组诗；不将元数据、注释或平仄标注当新作品 |
| 作者、标题、关键词、朝代等条件组合 | 可执行 SQLite 查询，作者与词牌精确匹配、标题/正文子串检索、明确分页与计数 |
| 注意唐诗多为繁体 | 用 OpenCC 归一化查询与索引，结果保留原文和异文 |
| 查询与生成两种意图，创作可参考数据库 | 纯查询带来源直接回答；需要参考时少量检索并提炼方法，不复制原句或借用原作事件 |

上游 setup.sh 将原库克隆到 Skill 内的 data/，并清除 .git 等文件；PROMPT.md 说明了字段映射和遍历策略，
没有独立的语义搜索服务或模型训练实现。本项目没有照搬其清理命令，而是保留可审核的源数据，
另建派生只读索引。上游作品数量是其声明，本项目以实际建库数量为准。
原库的 rank 热度、strains 平仄、其他重复版本未导入本次索引；语料命中不认证格律或审美。
互联网收集的文字与归属可能有异文或错误，不将作者简介与注释当作权威考证。

## ALDIFS/Poetry-meter-skill

- 项目：[ALDIFS/Poetry-meter-skill](https://github.com/ALDIFS/Poetry-meter-skill)。
- 阅读版本：[固定提交的 skill.md](https://github.com/ALDIFS/Poetry-meter-skill/blob/d404bb6671dab77ed61a515843903351590cbffd/skill.md)。
- 上游 Skill 自报版本：3.0；本次也阅读同一项目 README。
- 本项目的落地位置：`craft_revision.md` 及 compose / critique / revise / orchestration 的调用说明。
- 本次未找到明确的独立许可证文件；因此未复制原文、独特例句、韵表、格律模板或诗人风格表。
  这里只将一般写作思路独立组织为适合本项目的操作方法，并保留参考出处。

### 采用与调整

| 参考方向 | 在本项目中的实现 | 适用边界 |
|---|---|---|
| 从身体和动作承载感受 | 优先发现输入已有的反应，并核对语义是否保留 | 不强制器官或疼痛，不补造事实 |
| 精炼语句与词语 | 重组句子，比较关键动词与语义重心，保留原句对照 | 不按词类禁用白话，不为了古雅牺牲准确性 |
| 意象布局与虚实转换 | 核对视点、空间、时间及梦境线索 | 不限制意象数量，不因月与星共存判错 |
| 用典与化用 | 按需查原义、出处、实际用法与情感轻重，再决定是否采用 | 不把常见意象固定映射为情绪，不把换词当原创 |
| 结尾与转折的推敲 | 需要时比较不同收束方式，朗读检验衔接 | 不规定只能画面结尾，不删除必要的逻辑线索 |
| 完稿后自查 | 核对素材语义与朗读；修律后复查 | 不增加审美得分或自动进化机制，不拿模型自评作真人反馈 |

### 未采用

没有导入“古典形式只能使用古代物件”“每句/每首固定意象数量”“形容词一律不佳”
“刻意留下破绽”“韵部固定对应某种情绪”等普遍规则。
上游的声韵口诀、入声字表和模板没有替代姊妹项目的确定性检查。
上游 README 宣传的自动权重机制，在本次读取的 Skill 中未见对应的可执行持久化实现；
本项目不将它当成已验证能力，也不声称实现了模型训练或自动学习。
上游关于诗学理论及真人实践的归因没有被本项目独立验证，不转述为第三方审美背书。

## 既有来源

此前已经记录的研究与真人证据指针继续保留在各 protocol、reference 及
`runtime_teaching/` 文件中。本页不把外部参考或新生成的案例混入已有真人验证证据。
传统验律接入来自 wb14123/rhyme-checker，选择与使用边界见 `prosody_selection.md`
及姊妹项目的 `references/sources.md`、`references/traditional_backend.md`。
