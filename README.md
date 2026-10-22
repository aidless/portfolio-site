# portfolio-site

Public portfolio for AI application / Agent engineering roles.

**Live:** https://aidless.github.io/portfolio-site/

Four public demos, each with its own repository, CI, and honest boundaries:

| Demo | What it shows | Link |
|---|---|---|
| agent-platform | End-to-end ticket pipeline: gateway, sandbox, memory compression, observability | [Demo](https://aidless.github.io/agent-platform/) · [Source](https://github.com/aidless/agent-platform) |
| arx | Benchmark readability audit: READABLE / MARGINAL / UNREADABLE / UNDECIDABLE | [Demo](https://aidless.github.io/arx/) · [Source](https://github.com/aidless/arx) |
| agent-redteam | 12 attack vectors × 5 defense layers, layer coverage matrix | [Demo](https://aidless.github.io/agent-redteam/) · [Source](https://github.com/aidless/agent-redteam) |
| enterprise-rag | Retrieval evidence replay: negative results and ablations | [Demo](https://aidless.github.io/enterprise-rag/) · [Source](https://github.com/aidless/enterprise-rag) |

The site is a zero-dependency static page: no CDN, no external fonts, no
JavaScript, no tracking. This repository contains only the site; the demos
and their tests live in their own repositories.

## Run locally

```bash
python3 -m http.server -d site 8000
# open http://127.0.0.1:8000/
```

## License

MIT
