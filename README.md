# AI 应用工程作品集

> **English TL;DR**: A zero-dependency static portfolio site presenting three flagship evidence lines (agent-platform, llm-lab, study-buddy) with explicit boundaries. Its site contract checker validates cards, evidence numbers, local assets, zero JavaScript/CDN and the 5/5 offline PASS markers; the embedded llm-lab evidence is an offline demo, not a model-quality claim.

[![CI](https://github.com/aidless/portfolio-site/actions/workflows/pages.yml/badge.svg)](https://github.com/aidless/portfolio-site/actions/workflows/pages.yml)

**在线地址**：https://aidless.github.io/portfolio-site/ （GitHub Pages，2026-11-10 实测 HTTP 200）

![站点截图](docs/screenshot.png)

*截图：2026-11-10 本地 `python3 -m http.server 8020 -d site` 后 Chrome headless 1280×3200 实截（首屏 + agent-platform 卡 + llm-lab 报告节）。页面淡入动画未在 headless 中完全触发，成图偏浅，属如实状态。*

这是一个零依赖静态作品集，用三条旗舰证据线说明 AI 应用工程能力：

| 证据线 | 证明什么 | 不证明什么 |
|---|---|---|
| [agent-platform](https://github.com/aidless/agent-platform) | 网关、工具沙箱、记忆压缩、可观测与端到端失败分类 | 真实客服流量、真实 LLM 可用率、生产 SLO |
| [llm-lab](https://github.com/aidless/llm-lab) | 评测编排、输出验证、成本记录与哈希链审计可重放 | 模型质量、榜单名次、生产可靠性 |
| [study-buddy](https://github.com/aidless/study-buddy) | 移动端首次路径、任务状态持久化与明确的隐私选项 | 真实用户留存、消费级通过、云端稳定性 |

rag-qa 作为技术补充，展示混合检索、强制引用、证据不足拒答和离线复测。

## 当前状态

- 新版站点已完成本地构建、静态契约检查和浏览器验收。
- `main` 推送后，Pages workflow 会先运行静态检查，再发布 `site/`。
- 当前线上版本以对应 GitHub Actions run 和 Pages HTTPS 响应为准。
- study-buddy 当前真实用户为 **0**，首任务完成和 48 小时回访均为 **0/0**。
- 所有合成 Demo、离线 Provider、小样本评测和未验证项都在页面中主动标注。

## 本地运行

```bash
python3 -m http.server 8020 -d site
# open http://127.0.0.1:8020/
```

## 静态检查

```bash
python3 tools/check_site.py
```

检查器验证三张项目卡、证据数字、全部本地资源、零 JavaScript、零 CDN、
响应式/打印/减少动效契约，以及 llm-lab 报告中的 5 个 PASS 标记。

## 图片与证据

`site/assets/` 中三张预览图来自本机 Chromium 截图后转成 WebP；不包含账号、
密钥、真实用户输入或私有数据。`site/evidence/` 只放可公开检查的 llm-lab
离线报告与结果 JSON。截图只证明视觉与交互路径，不证明用户留存或生产可靠性。

## 部署边界

GitHub Pages workflow 会在推送后先运行静态检查，再发布 `site/`。发布结果只由
对应 Actions run、部署记录和公开 HTTPS 响应确认。

## License

MIT

## U1 results table (recomputed 2026-11-11)

<!-- figure: docs/screenshot.png (existing screenshot; a fresh capture is NOT YET MEASURED in this pass) -->

All values below were recomputed from the committed evidence JSON, and the site
checker was executed locally for this pass.

| Result | Value | Source (path:line) |
|---|---|---|
| Evidence run id | `df0c8ed1379c` | `site/evidence/llm-lab-result.json:2` |
| Model (offline) | `offline-demo-v1` | `site/evidence/llm-lab-result.json:5` |
| Verifier | `structural` | `site/evidence/llm-lab-result.json:6` |
| Steps recorded | 5 | `site/evidence/llm-lab-result.json:7` |
| Step detail entries | 5 | `site/evidence/llm-lab-result.json:9` |
| Verdict labels | pass=5 | `site/evidence/llm-lab-result.json:16` (counted from `steps_detail[].verdict.label`) |
| Total tokens | 185 | `site/evidence/llm-lab-result.json:76` |
| Total cost (USD) | 0.0 | `site/evidence/llm-lab-result.json:77` |

**Quickstart command actually executed for this pass** (exit code 0):

```bash
python3 tools/check_site.py
# PASS  site contract: 3 flagship cards, 4 evidence rows, local assets, boundaries
# PASS  zero JavaScript, zero CDN, responsive/print/reduced-motion CSS contracts
# PASS  llm-lab evidence: 5/5 PASS, $0.000000, 5 visible report badges
```

The screenshot already embedded above is a real local headless-browser capture;
no new figure was fabricated for this pass. The offline provider gives
`model: offline-demo-v1` and `total_cost_usd: 0.0` — cost and
quality numbers here are demo artifacts, not production measurements.
