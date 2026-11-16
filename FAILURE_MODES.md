# FAILURE_MODES

`make check` proves the site matches the committed snapshots. It does not prove the upstream repositories re-ran those tests today, and it does not prove this portfolio is grade A.

## 摘录会过期

`evidence/sources.json` 把每条数字钉在上游默认分支的一个 commit 上，并保存当时的原文。`make check` 离线，只比较本仓的页面、JSON 和 `evidence/snapshots/`。上游 main 之后再改 README 或结果文件，本仓不会自动变红。要发现这种漂移，需要有网络时跑 `make refresh`。它只打印差异，不改文件。没人把新摘录提交进来之前，页面可以继续引用已经过时的句子。

## 未合并的上游 PR

下面这些 PR 在 2026-11-16 仍是开放的。页面跟随各仓默认分支，不跟随 PR 分支。

| 仓库 | PR | 合并后会怎样 |
|---|---|---|
| agent-platform | [#2](https://github.com/aidless/agent-platform/pull/2) `57376669267c` | 删掉 `10/10 模块 PASS` 这句，把回放改成 65 条 PASS、2 条预期失败、7 条说明。`demo/test_demo.py` 仍是 16 个测试方法，没有 16 项全过的记录。 |
| llm-lab | [#5](https://github.com/aidless/llm-lab/pull/5) `18213a85de67` | 把 `419 passed / 2 skipped` 和 `106 passed` 改成时点记录；`docs/test-inventory.json` 写产品包 421 passed / 2 skipped、根套件 collected 112。去掉 `488 passed / 2 skipped` 与 `382 passed / 2 skipped`，也去掉 `ruff and mypy clean` 那句 changelog。 |
| study-buddy | [#11](https://github.com/aidless/study-buddy/pull/11) `238ceb0847de` | README 不再写 `Tests 11 passed` 和 `ALL_OK`。`docs/user-validation-status.md` 里的真实用户 0、首任务 `0/0`、48 小时 `0/0` 不变。 |
| rag-qa | [#1](https://github.com/aidless/rag-qa/pull/1) `e0d49a8ae0dc` | 不再写 `6 passed`。README 表和 `results/eval-offline.jsonl` 仍是 fixed `9/12`、structure `10/12`、两组拒答 `4/4`。 |

`make refresh` 会再拉这些 head。若某个 PR 后来把原文加回去或删掉，而 `quote_on_head` 还是旧的布尔值，refresh 以退出码 1 报告，不会静默。

## 截图会过期

`docs/screenshot.png` 在 2026-11-16 用本机 `python3 -m http.server 8020 -d site` 和 Chrome headless（1280×3200，`virtual-time-budget=4000`）重拍过。它只覆盖页面顶部，能看见 agent-platform 卡上的新摘录句，看不见底部账本。下一次改 `site/index.html` 的可见句子后，这张图又会过期，除非重拍并改 README 里的日期。

## 上游文档自己打架

llm-lab 的 `42027f21594b` 上，CHANGELOG 与包 README 写产品包 419，根套件 106；`llm_lab/docs/ARCHITECTURE.md` 写全仓 488 passed / 2 skipped、子树 382 passed / 2 skipped，并声称这与徽章一致。本站把冲突原样写上，不挑选一个更大的数字。这些都是文件里的句子，不是本仓重新执行 pytest 的结果。

## 公开站落后于分支

GitHub Pages 只发布默认分支上的 `site/`。2026-11-16 对 https://aidless.github.io/portfolio-site/ 的 GET 返回 200，正文 sha256 `c13142cc8e5938c436001ed4deb4bb5d15e841276e0ef5a7c4adebf09cf92ac6`，与当时 `main` 的 `site/index.html` 相同。本分支合并并部署之前，线上页面仍是旧数字。

## 本仓自己的开放 PR

2026-11-16 本仓开放的是 Dependabot 的 [#1](https://github.com/aidless/portfolio-site/pull/1)（`actions/upload-artifact` 4.6.2 → 7.0.2）和 [#3](https://github.com/aidless/portfolio-site/pull/3)（`actions/checkout` 4.4.0 → 7.0.1）。它们不改证据数字。这次没有合并它们。
