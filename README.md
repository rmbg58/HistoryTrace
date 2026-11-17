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

---

*调研完成于 2026-11-18,star 数与平台状态均为当日核实值。*
