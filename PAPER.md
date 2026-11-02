# portfolio-site：零依赖静态作品集与诚实证据线

> 本文档是 portfolio-site 的**论文摘要草稿**，内容全部来自仓库真实实现与实测结果，
> 无虚构数字。

## 摘要（Abstract）

一份求职作品集要能**站得住**：它证明什么、不证明什么必须逐条分明，否则读者会把
"Demo 能跑"误读成"生产可用"。本文构建一个**零依赖静态作品集**，用三条旗舰证据线
说明 AI 应用工程能力，每条都同时声明"证明什么"与"不证明什么"。

**三条证据线**：
- **agent-platform**：证明网关、工具沙箱、记忆压缩、可观测与端到端失败分类；
  不证明真实客服流量、真实 LLM 可用率、生产 SLO。
- **llm-lab**：证明评测编排、输出验证、成本记录与哈希链审计可重放；不证明模型
  质量、榜单名次、生产可靠性。
- **study-buddy**：证明移动端首次路径、任务状态持久化与明确的隐私选项；不证明
  真实用户留存、消费级通过、云端稳定性。

**诚实声明（关键）**：study-buddy 当前真实用户为 **0**、首任务完成和 48 小时回访
均为 **0/0**；所有合成 Demo、离线 Provider、小样本评测和未验证项都在页面中主动
标注。llm-lab 的成本 `$0.000000` 是离线 Provider 的零成本 demo（`llm-lab-result.json`
的 `all_passed==true`、`total_cost_usd==0.0`、5 步全 `pass`），非真实计费。

**验证（可复算）**：`tools/check_site.py` 是唯一自动验证入口（零依赖、确定性、可
离线跑），实测 3 行 PASS：
- `site contract`：3 张旗舰卡、4 行证据、全部本地资源、边界声明存在；
- `zero JavaScript, zero CDN`：零 `<script>`、零外部资源、响应式/打印/减少动效
  CSS 契约；
- `llm-lab evidence`：`steps==5`、`all_passed==true`、`total_cost_usd==0.0`、
  5 个 verdict 全 `pass`、报告 5 个 PASS 徽章可见。

**fail-closed（关键行为）**：检查器在任一契约违反时返回 exit 1（FAIL）——缺文件、
缺 id、过期文案（`FORBIDDEN_TEXT`）、卡片数不对、出现 `<script>`/外部资源、证据
JSON 非法、出现 API key（`sk-` 模式）/GitHub token（`gh[pousr]_`）/绝对 home 路径
（`/home/`、`/Users/`、`C:\`），全部被拦下。这是诚实度量：坏的站点产生 FAIL，而
不是静默放行。

**明确边界**：本站点**不证明**任何真实用户留存（0/0）、**不证明**生产可用率或
SLO（未接入监控）、**不证明**截图之外的视觉/交互价值；截图只证明视觉与交互路径。

## 关键词

作品集；静态站点；证据线；fail-closed；零依赖；求职；诚实边界；可复算检查

## 与真实代码的对应

| 摘要声明 | 对应真实实现 |
|---|---|
| 3 张旗舰卡 | `site/index.html`（3 个 `<article class="project">`） |
| 零依赖 | `site/`（index.html + style.css + assets/ + evidence/，无 `<script>`） |
| 证据 JSON | `site/evidence/llm-lab-result.json`（5 步全 pass、$0.000000） |
| 检查器 | `tools/check_site.py`（exit 0/1 fail-closed） |
| 3 行 PASS | `python3 tools/check_site.py` 实测 3 行 PASS |
| 证据数字 | `16/16`、`391 passed`、`10/12`、`0 个真实用户`（在 index.html） |
