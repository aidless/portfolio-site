# PREREG — portfolio-site 预注册规格

> 本文件是 portfolio-site（零依赖静态作品集站点）的**预注册规格**：把研究假设、
> 评测方案、成功标准与明确边界写在分析之前。所有数字可从仓库内确定性代码/
> 检查器实测复算。

## 1. 研究问题

一份求职作品集要能**站得住**：它证明什么、不证明什么必须逐条分明，否则读者会把
"Demo 能跑"误读成"生产可用"。

**核心假设（H1）**：零依赖静态站点可用**三条旗舰证据线**说明 AI 应用工程能力——
agent-platform（网关/工具沙箱/记忆压缩/可观测/端到端失败分类）、llm-lab（评测编排/
输出验证/成本记录/哈希链审计可重放）、study-buddy（移动端首次路径/任务状态持久化/
隐私选项）——每条都同时声明"证明什么"与"不证明什么"。

**辅助假设（H2，fail-closed）**：静态检查器（`tools/check_site.py`）在任一契约
违反时返回 exit 1（FAIL）——缺文件、缺 id、过期文案、卡片数不对、出现 JS/外部
资源、证据 JSON 非法、出现 API key/GitHub token/绝对 home 路径，全部被拦下。

**辅助假设（H3，诚实声明）**：study-buddy 当前真实用户为 **0**、首任务完成和
48 小时回访均为 **0/0**；所有合成 Demo、离线 Provider、小样本评测和未验证项都
在页面中主动标注。

## 2. 评测方案（可复算）

### 2.1 静态契约检查（唯一自动验证入口，零依赖、确定性、可离线）

```bash
python3 tools/check_site.py
```

实测输出（3 行 PASS）：

```
PASS  site contract: 3 flagship cards, 4 evidence rows, local assets, boundaries
PASS  zero JavaScript, zero CDN, responsive/print/reduced-motion CSS contracts
PASS  llm-lab evidence: 5/5 PASS, $0.000000, 5 visible report badges
```

断言明细：
- **site contract**：3 张旗舰卡、4 行证据、全部本地资源、边界声明存在。
- **zero JS/CDN**：零 `<script>`、零外部资源、响应式/打印/减少动效 CSS 契约。
- **llm-lab evidence**：`llm-lab-result.json` 的 `steps==5`、`all_passed==true`、
  `total_cost_usd==0.0`、5 个 verdict 全 `pass`；报告 5 个 PASS 徽章可见。

### 2.2 证据数字（真实）

`tools/check_site.py` 的 `REQUIRED_TEXT` 断言 `site/index.html` 必须包含：
`16/16`（agent-platform）、`391 passed`（llm-lab）、`10/12`、`0 个真实用户`
（study-buddy）。这些数字来自各证据线的真实产物，可在此树复算。

### 2.3 成功标准

| 判据 | 成功标准 |
|---|---|
| 静态检查 | `check_site.py` = 3 行 PASS（exit 0） |
| 证据完整 | 3 张旗舰卡 + 4 行证据 + 5/5 PASS + $0.000000 |
| fail-closed | 任一契约违反 → exit 1（不静默放行） |
| 诚实声明 | 真实用户 0、48h 回访 0/0 在页面主动标注 |

## 3. 明确边界（不证明什么）

1. **不证明任何真实用户留存**——study-buddy 当前真实用户为 **0**，48 小时回访
   **0/0**。
2. **不证明生产可用率或 SLO**——站点未接入任何监控。
3. **不证明截图之外的视觉/交互价值**——截图只证明视觉与交互路径，不证明用户
   留存或生产可靠性。
4. **不证明 llm-lab 模型质量/榜单名次**——`$0.000000` 是离线 Provider 的零成本
   demo，非真实计费。
5. **不证明真实客服流量/真实 LLM 可用率**（agent-platform 边界）。

## 4. 成功标准（判据）

本预注册声明**成功**当且仅当：
1. `python3 tools/check_site.py` 输出 3 行 PASS（exit 0）；
2. 三条证据线的"证明/不证明"都出现在页面边界声明中；
3. fail-closed 行为有断言覆盖（任一违反 → exit 1）；
4. 每一条"不证明"边界都在 README「证明什么/不证明什么」或本文件有对应记录。
