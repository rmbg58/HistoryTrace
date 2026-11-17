# HistoryTrace 项目总体规划

版本:v0.1(2026-11-18)
配套文档:[校验机制](verification-protocol.md) | [调研一:地图与 GIS](research/01-map-gis-projects.md) | [调研二:诗词与人物](research/02-poetry-people-data.md) | [调研三:古籍与校勘](research/03-guji-platforms-collation.md)

---

## 1. 愿景与范围

**做一个"可信"的中国历史时空互动平台**:从先秦到今天,便捷切换朝代/年份,点选任一地点看到历代名称与政区沿革;后续叠加历史事件、诗人足迹 + 作品 + 时空线索。

与既有产品的差异化定位:

| 既有 | 缺口 |
|---|---|
| 发现中国/地图书(协作矢量化) | 无逐条来源溯源,无校验状态 |
| jiangshan-map(7.6k★,交互最全) | 数据不可再分发(CHGIS 派生),无事件/诗人深做 |
| 搜韵·唐宋文学编年地图(王兆鹏团队,151 诗人) | 数据封闭,无 API,仅唐宋 |
| CHGIS(学术标准数据) | 禁再分发,面向学者非公众 |

**本项目的护城河 = 自建的、声明式(attestation)的、经多来源多轮次校验的开放数据**——代码不是壁垒,数据可信度才是(调研结论:诗人足迹方向开源生态最高相关项目仅 0 star)。

## 2. 调研关键结论(决策依据)

1. **许可红线决定数据架构**:CHGIS(禁商用/再分发)、CBDB(CC BY-NC-SA + 大陆商用独占授权)、谭图扫描件(版权)、中华书局点校本(2012 胜诉判例)——都不能作为可分发数据。**可分发**的只有:WHG(CC-BY-4.0)、Cliopatria 边界(Apache-2.0)、维基文库文本(CC-BY-SA)、chinese-poetry(MIT)、GeoNames(CC-BY)、6tail/lunar-*(MIT)、ming-zhengshuo(MIT)。
2. **最大数据缺口是"作品级系年"与"诗人精细年谱"**:chinese-poetry 无任何时空字段;CBDB 只有生涯事件级地址;开源世界无年谱数据集。必须自建(公版古籍 + LLM 抽取 + 人工校对)。
3. **交互范式已被验证可行**:jiangshan-map 的"年份→快照 + 点选 Trace Place"完全覆盖 MVP 需求;MapLibre 是无 token 的开源渲染首选。
4. **校验方法论有成熟蓝本**:陈垣四校法 + WHG attestation 模型 + OpenRefine reconciliation 实践 → 已形式化为 [verification-protocol.md](verification-protocol.md)。

## 3. 总体架构

```
┌─ 外部来源(不直接入库)──────────────────────────────────────┐
│ 维基文库 API · ctext 点查 · CHGIS(本地) · CBDB sqlite · WHG ·   │
│ Cliopatria · chinese-poetry · GeoNames · 影印善本(人工)        │
└──────────────┬───────────────────────────────────────────┘
               │ ETL(Python:清洗/抽取/纪年换算/几何处理)
               ▼
   data/claims/  ← 声明库(git 版本化,每条带来源+置信+裁决)
               │
               ▼ 校验流水线(ht verify:R0→R1→R2 → PR 人工复核 → R4 回归)
               │
               ▼ 构建产物(ht build)
   public/data/  · 沿革索引 JSON · PMTiles 瓦片 · 作品/人物/事件 JSON
               │
               ▼
   前端(MapLibre + PMTiles + 时间轴 + 沿革卡片 + 溯源面板)→ 静态部署
```

要点:**claims 是唯一事实源(single source of truth)**,一切展示层(瓦片、索引、API)都是其派生物,可随时重建;来源不进仓库,只进登记(Source 注册表)与引文(quote)。

## 4. 核心数据模型(摘要)

实体:`Place`(现代锚点,WGS84 坐标)、`Polity`(政权/王朝)、`Person`、`Work`(作品)、`Event`;关系全部以 Claim 表达(谓词表见校验协议 §1.2):

- **地点历代名称卡片**(MVP 核心)= 一个 Place 聚合其全部 `name_in_period` / `belongs_to` claim,按时间排序,附置信度与异说;
- **朝代切换** = 按年份选取 `boundary_snapshot`(可分发几何)+ 该年生效的 claims;
- **诗人足迹** = `Person` 的时间排序 `person_at` 序列 + `Work` 的 `written_at/when`;
- **事件层** = `Event` 的 `occurred_at/when` + 类型标签。

## 5. 许可策略(⚠ 最重要的早期决策)

| 用途 | 允许进入发布产物 | 仅本地/人工参照(不随仓库分发) |
|---|---|---|
| 地名沿革/文本 | 维基文库(CC-BY-SA)、chinese-poetry(MIT)、自建 claims | ctext(点查+URN)、识典(人工)、殆知阁(旁证)、**中华书局点校本(只参校)** |
| 几何边界 | WHG(CC-BY)、Cliopatria(Apache-2.0)、自绘 | **CHGIS(本地开发校验用)**、谭图(不使用) |
| 人物数据 | Wikidata(CC0) | **CBDB(本地校验参照)** |

**决策已定(2026-11-18,ADR-002)**:代码 MIT + 自建数据 CC BY-SA 4.0(允许他人遵相同方式共享地商用);**暂不走学术合作授权路线**,CHGIS/CBDB 均按"本地参照"使用。许可文件已落地(LICENSE、DATA-LICENSE.md);devinit standard 治理体系已建立(docs/gov/)。若未来需要商用收紧或申请学术授权,走新 ADR。

## 6. 技术选型

| 层 | 选择 | 理由/参考 |
|---|---|---|
| 前端框架 | TypeScript + Vite + 原生组件(或轻量框架) | jiangshan-map 证明原生 JS 可承载;避免重框架 |
| 地图渲染 | **MapLibre GL JS** | 开源无 token;MapStage(MIT)为叙事模板 |
| 瓦片分发 | **PMTiles**(单文件静态托管) | 无服务器成本,适配历史快照按需加载 |
| 时间交互 | "年份→快照"范式 + 时间轴 scrub | 参考 jiangshan-map index.json 设计(**只参考范式,代码自研**,规避 GPL 传染与数据污染) |
| 数据处理 | Python 3.12 + geopandas/shapely/pyproj + Click(CLI:`ht verify` / `ht build`) | |
| 文本比对 | 按字 token + difflib(起步)→ CollateX(GPL,进程隔离调用) | |
| OCR(后期) | PP-OCRv5(繁体/竖排) | 自建年谱语料时用 |
| 存储 | git 版本化 JSON/YAML(claims)+ SQLite(派生缓存) | 数据即代码,PR 即复核 |
| CI | GitHub Actions:PR 上自动跑 R1 机器校验 | 校验协议 §6 |
| 纪年 | ming-zhengshuo(MIT)+ CBDB 年号表交叉验证 + lunar-python(MIT,干支) | |
| 部署 | 静态站(GitHub Pages/Cloudflare Pages) | |

## 7. 路线图

### P0 基础设施(≈1–2 周)
- [x] 定许可证(ADR-002:代码 MIT + 数据 CC BY-SA)+ `git init` 基线提交 + devinit 治理体系(docs/gov/、AGENTS.md)+ 古风设计系统规范(05-DESIGN.md)
- [ ] 仓库骨架(pipelines/ web/ data/)
- [ ] Claim/Source JSON Schema + 校验器(协议 §1 落地为 schema)
- [ ] CLI 骨架:`ht import-wikisource`(廿四史地理志样例)、`ht verify`(R0+R1)
- [ ] **种子数据走通全流程**:10 个锚点城市(西安/洛阳/南京/北京/成都/苏州/广州/武汉/杭州/开封)× 5 个朝代(汉/唐/宋/明/清)手工+机器混合录入,每条带至少 2 来源
- 验收:种子集 R0–R3 全链路有产物;`ht build` 产出第一版沿革索引 JSON

### P1 MVP:地图 + 朝代切换 + 点选沿革(≈1–2 月)
- [ ] Cliopatria 边界提取中国政权几何 → PMTiles;朝代/年份时间轴 UI
- [ ] MapLibre 地图 + 点选 → 沿革卡片(名称时间线 + 置信角标 + 溯源面板)
- [ ] GeoNames/WHG 对齐管道(L5);维基文库地理志批量对校(L1)
- [ ] 府级地名扩展:优先 200–300 个州府级锚点
- 验收:切换顺滑(<100ms 层切换);任一种子地点可看 ≥5 朝代名称;每个名称可展开来源

### P2 历史事件层(≈1 月,可与 P3 并行)
- [ ] Event schema + 种子事件集(统一/分裂、迁都、安史之乱、靖康、条约割地、改省…)
- [ ] 事件多史互证管道(L3);时间轴事件标记 + 点击地图落点
- [ ] 事件与地名沿革联动(如"某年改名为 X,因事件 Y")

### P3 诗人足迹 + 作品 + 时空线索(持续)
- [ ] 10 位种子诗人(李白/杜甫/苏轼/王维/白居易/陆游/柳宗元/韩愈/李清照/辛弃疾)精细年谱:CBDB(本地参照)+ 公版年谱 + 诗题诗注抽取("年-地-事"三元组)
- [ ] 作品库接入 chinese-poetry(MIT);**系年管道**(L3+L4,默认 G2 以下,编年笺注依据才升级)
- [ ] 行迹地图:路线动画、按年播放、作品气泡(地点→该地所作诗词)
- [ ] 地名消歧:别名表 + 歧义裁决 + 虚写排除(借鉴 poetry-map schema,重新整理)
- 验收:任一种子诗人可播放生平行迹,每站有事件与作品,系年有依据链

### 持续项
- R4 回归自动化(来源更新监听);数据质量报告页;贡献者指南(复核队列玩法,借鉴识典"任务分发 + 署名"激励)

## 8. 风险与对策

| 风险 | 对策 |
|---|---|
| 许可违规(最大风险) | 协议 §9 红线清单进 CI 检查;发布产物只含白名单来源;PR 模板强制许可自查 |
| 学术争议被质疑 | 冲突不合并 + 置信分级 + 异说展示;理校永不定论;每条可溯源 |
| 数据工程量巨大 | 种子示范 → 流水线自动化 → 众包(PR 复核);先深度(10 城×5 朝)后广度 |
| LLM 抽取错误率 | 一切机器产物 tier E、G1 起步;OCR 置信分进机器分;人工裁决才可升级 |
| ctext/识典反爬 | 只点查不批量;以维基文库为批量基准语料 |
| 单人维护不可持续 | 数据即代码 + 清晰贡献指南 + 复核队列低门槛(单条 claim 粒度) |

## 9. 立即可做的下一步

1. ~~确认许可决策~~ 已定:代码 MIT + 数据 CC BY-SA,不走学术合作(ADR-002);
2. ~~git init + 提交 docs~~ 已完成基线提交;治理体系(devinit standard)与古风设计系统(05-DESIGN.md)已建立;
3. 写 Claim JSON Schema 与 `ht verify` R0 规则(许可白名单检查);
4. 手工录入第一批种子 claim(西安"长安"条目可直接采用协议 §1.2 示例),跑通 R0–R1;
5. 拉 Cliopatria 中国几何 + 维基文库《汉书·地理志》开始 P1 数据管道。
