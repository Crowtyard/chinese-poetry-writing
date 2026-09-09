# Chinese Poetry Writing

中文诗歌创作 Skill。提供从发现诗眼到成稿、批评、修改的完整创作方法，不绑定任何具体人格。

## 主要能力

- **COMPOSE**：构思与创作（FACT → IRREPLACEABLE_FACT → DISCOVERY → RELATION → CONCEPT → DRAFT）
- **CRITIQUE**：审美诊断（物证在场 / 关系做功 / 自然度 / 解释度 / 技巧可见度 / 不可替换性）
- **REVISE**：修改诗稿（保诗眼优先，逐层修订，禁止以律害意）
- **ORCHESTRATE**：调度完整创作流程（迭代上限、验律协作、输出纪律）

## 核心工作流

```
FACT
→ IRREPLACEABLE_FACT
→ DISCOVERY
→ RELATION
→ CONCEPT
→ DRAFT
→ CRITIQUE
→ REVISE
→ PROSODY
→ FINAL CHECK
```

## 职责边界

本 Skill 不负责确定性诗律计算（拼音 / 平仄 / 押韵 / 相对 / 相粘 / 韵部）。

格律检查由独立项目负责：

https://github.com/Crowtyard/chinese-poetry-prosody

推荐架构：

```
Persona
→ chinese-poetry-writing
→ chinese-poetry-prosody
```

- Persona：负责人格、经历、视角、声音。
- chinese-poetry-writing：负责构思、创作、批评、修改。
- chinese-poetry-prosody：只负责确定性验律。

## 版本

v0.1-beta

## 状态

REAL_USER_BETA

当前版本经过 10 个 smoke tests，10 PASS / 0 WARN / 0 FAIL，
但 Beta 状态不代表审美模型已经完备。
