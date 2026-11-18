# HistoryTrace · 历史长河

中国历史地图时空变迁互动项目:从先秦到今天,按朝代/年份便捷切换疆域与政区,点选任一地点查看其**历代名称沿革**;后续叠加**历史事件**、**诗人足迹 + 作品 + 时空线索**。所有数据建立在**多来源、多轮次校验机制**之上,可信度分级展示。

## 文档导航

| 文档 | 内容 |
|---|---|
| [docs/project-plan.md](docs/project-plan.md) | 总体规划:愿景、架构、数据模型、技术选型、路线图、风险 |
| [docs/verification-protocol.md](docs/verification-protocol.md) | **核心**:多来源多轮次校验机制设计 |
| [docs/research/01-map-gis-projects.md](docs/research/01-map-gis-projects.md) | 调研:历史地图开源项目与 GIS 数据源 |
| [docs/research/02-poetry-people-data.md](docs/research/02-poetry-people-data.md) | 调研:诗词文本、人物行迹、纪年换算数据 |
| [docs/research/03-guji-platforms-collation.md](docs/research/03-guji-platforms-collation.md) | 调研:古籍平台、OCR 工具、校勘方法论 |

## 核心原则

1. **每条数据都是带来源的"声明"(attestation)**——cite your sources for every claim(借鉴 World Historical Gazetteer 模型)
2. **冲突不合并**:不同来源的矛盾陈述共存,展示"当前采信值 + 异说"
3. **机器只降级、不升级**:升到"已验证"必须有人工裁决记录(借鉴 OpenRefine/Wikidata reconciliation 实践)
4. **理校永不自动定论**:LLM/规则推理只产出"校勘建议",必须人工裁决(陈垣:"最高妙者此法,最危险者亦此法")
5. **许可红线**:中华书局点校本只参校不转录;CHGIS/CBDB 仅本地参照、不随项目再分发;公开分发的数据只用干净许可(WHG CC-BY-4.0 / Cliopatria Apache-2.0 / 维基文库 CC-BY-SA / chinese-poetry MIT / GeoNames CC-BY)

## 阶段目标

- **P0 基础设施**:数据 schema、校验流水线骨架、种子数据跑通全流程
- **P1 MVP**:互动地图 + 朝代/年份切换 + 点选地点看历代名称
- **P2**:历史事件图层(时间、地点、来源、置信度)
- **P3**:诗人足迹 + 作品系年 + 时空线索(行迹动画、作品气泡)

## 许可

- 代码:**MIT**([LICENSE](LICENSE))
- 自建数据(`data/`):**CC BY-SA 4.0**([DATA-LICENSE.md](DATA-LICENSE.md))
- 第三方来源按 `data/registry/` 白名单;CHGIS/CBDB 等受限数据仅本地参照、不入库(ADR-002)

## 工程治理

devinit standard 治理体系位于 `docs/gov/`(STATE/概览/架构/规范/模块/ADR/设计系统);Agent 会话入口:[AGENTS.md](AGENTS.md)。UI 采用古风设计系统(宣纸·墨·朱砂),规范见 [docs/gov/05-DESIGN.md](docs/gov/05-DESIGN.md)。

## 快速上手

```bash
# 数据管线(Python,uv)
cd pipelines
uv sync                        # 安装依赖
uv run ht verify               # R0 许可白名单 + R1 一致性校验
uv run ht build                # claims → web/public/data 静态产物
uv run ht report               # 数据质量报告
uv run ht proofread --dyn han --limit 20   # L1 对校(维基文库 insource)
uv run ht backfill --dyn han --limit 5     # 引文回填(命中页真实原文→复核队列)
uv run ht regression            # R4 回归(cross-checked 引文重检)
uv run ht era 贞观 14          # 年号纪年换算 → 640
uv run pytest                  # 数据管线测试

# 前端(pnpm)
cd ../web
pnpm install
pnpm dev                       # 开发预览(先跑过 ht build)
pnpm typecheck && pnpm test && pnpm build
```

当前进度(M1–M14 已完成):**161 个锚点城市**(含辽中京、西夏兴庆府、西域安西四镇、渤海国上京等跨政权条目)+ 10 条大史事 + **15 位诗人** 67 站行迹 + 39 首名作系年 = **701 条 claims**(G4 已验证 371);L1 对校→引文回填(511 条真源引文在档)→R4 回归(27/27 稳定)全链路闭环,复核队列(docs/gov/threads/review-queue.md)持续消化。交互支持:

- 朝代/年份切换:Cliopatria 疆界快照(墨线+淡彩,前朝幽灵虚线)+ 151 城古名联动
- 点选城邑:历代名称沿革卡,展开来源佐证笺注(部分已回填真实引文,cross-checked)
- 事件层:大史事朱印落点,当朝高亮;点看摘要与佐证
- 诗人足迹:李白/杜甫/王维/白居易/苏轼/陆游/柳宗元/韩愈/李清照/辛弃疾,行迹随时间轴渐显,可播放;作品墨笺气泡(系年 claim 化,G2 诚实)

**双平台已上线**:
- Cloudflare Pages(国内访问推荐):https://historytrace.pages.dev/
- GitHub Pages:https://rmbg58.github.io/HistoryTrace/

CI 自动构建发布,R4 每周回归。锚点 160 城,后续按省分批推进 200+。

---

*调研完成于 2026-11-18,star 数与平台状态均为当日核实值。*
