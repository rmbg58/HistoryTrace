# 决策日志(ADR)

> Append-only:只增不改不删。新 ADR 追加到文件末尾,编号递增。

当前生效规则以 manifest 指向的架构、规范和宿主入口为准。新 ADR 修订旧决策时写明被取代的 ADR 编号和生效范围;保留旧记录只用于追溯,不表示旧规则继续生效。

## ADR-001: 初始化技术选型(2026-11-18)

- **背景**:项目启动,确定基础技术栈与治理规则(基于 2026-11-18 三路调研,见 docs/research/)。
- **决策**:纯前端静态站 + 数据管线 CLI 双模块架构。前端 Vite + 原生 TypeScript(无框架无组件库)+ MapLibre GL JS + PMTiles;数据管线 Python(≥3.12,uv)+ `ht` CLI;数据即代码(data/claims git 版本化,PR 即复核);测试 vitest + pytest;治理 profile standard。
- **备选**:放弃 Next.js/Vue(无 SSR/后端需求,框架是负担);放弃 fork jiangshan-map(GPL-3.0 传染 + 其 CHGIS 派生数据不可再分发,只参考其交互范式);放弃 dev-kit Bases(实验性 admin/user-web 壳与古风静态站不匹配)。
- **影响**:全部模块;详见 00-OVERVIEW.md / 01-ARCHITECTURE.md / 02-CONVENTIONS.md。
- **维护与退出**:产物纯静态可任意托管;claims 纯 JSON 可导出;无数据库锁定。理解成本低(双语言但各自极简)。
- **模板基线**:none;kit 关联 personal-dev-kit@0.1.0(仅资产索引,未装配)。
- **取代**:无。

## ADR-002: 许可与数据合规策略(2026-11-18)

- **背景**:调研确认 CHGIS/CBDB/谭图扫描/中华书局点校本均不可再分发或转录(法律风险,见 docs/research/01、03);需决定项目许可与数据边界。
- **决策**(用户已确认):代码 MIT(LICENSE);自建数据(data/)CC BY-SA 4.0(DATA-LICENSE);**暂不走学术合作授权路线**(不向 CHGIS/CBDB 申请正式授权,均按"本地参照"使用)。发布产物只含白名单来源(WHG CC-BY / Cliopatria Apache-2.0 / 维基文库 CC-BY-SA / chinese-poetry MIT / GeoNames CC-BY);受限来源只存 `data/_downloaded/`(gitignore);点校本只参校不转录。
- **备选**:CC BY-NC(禁商用)被否——用户按推荐采纳 CC BY-SA(允许他人遵 SA 商用,利于数据生态);学术合作路线明确搁置,若未来需要可再启(新 ADR)。
- **影响**:data/registry 白名单是硬约束,进 CI;所有数据任务。
- **维护与退出**:白名单变更必须走新 ADR(法律风险级);受限数据若未来获授权,可提升其在 registry 的 tier。
- **取代**:无。

## ADR-003: 前端原生 TS 路线与古风 UI 体系(2026-11-18)

- **背景**:需定前端实现层次与视觉体系;用户明确"UI 风格要有古风的格调"。
- **决策**(用户已确认):Vite + 原生 TS(面试选定);无 UI 组件库、无 CSS 框架,原生 CSS + @layer + tokens.css;古风设计系统(宣纸/墨/朱砂色谱、楷宋字体栈、印章式置信角标)落 05-DESIGN.md;图标全自绘 SVG;部署平台待定(OT-001)。
- **备选**:Preact/Vue(组件化收益 < 引入运行时与默认风格成本);Tailwind(utility 体系与古风强定制 tokens 路线相比无优势)。
- **影响**:web/ 全部实现;05-DESIGN.md 为视觉事实源。
- **维护与退出**:无框架锁定,迁移到任何组件方案成本低;字体从系统栈起步,自托管思源系(OFL)留 OT-002。
- **取代**:无。

## ADR-004: M1 实现细节:依赖与地图标记方案(2026-11-18)

- **背景**:M1 开发落地时需定具体依赖与实现方式。
- **决策**:
  1. web 依赖仅 `maplibre-gl@^5`(运行时)+ vite/typescript/vitest(开发);PMTiles 包待 M2 接边界瓦片时再引入(避免未使用依赖)。
  2. 城邑标记用 **HTML Marker**(墨点 + 楷体标签)而非地图 glyph 文本层——规避 glyphs 服务依赖,标签样式(古名/都城朱砂)完全由项目 tokens 控制;10–300 城规模下性能足够,过量后再迁 symbol 层。
  3. 底图 = 纯宣纸色 background 层(无瓦片服务),M2 接 Cliopatria 疆界几何前保持离线可用。
  4. `#map` 布局用 `position:relative; width/height:100%`——maplibre 自带 CSS(unlayered)强制 `.maplibregl-map` relative,layered 的 absolute/inset 会被其压过(实测踩坑)。
  5. 种子 claims 由 `pipelines/scripts/gen_seed.py` 一次性生成落库;claims 文件本身是事实源,脚本仅作回归重建。
  6. 明/清朝代边界按"1644 归清"建模(明 latest=1643),时段区间含端点、不允许重叠(R2 冲突检测实测拦截过该问题)。
- **备选**:symbol 文本层(需 glyphs URL,离线不可用);absolute 布局强行 !important(破坏层叠体系)。
- **影响**:web/src/map/stage.ts、web/src/styles/app.css、pipelines/scripts/gen_seed.py。
- **维护与退出**:marker 方案在城邑数 >500 或需要避让算法时迁移 symbol 层;依赖升级常规。
- **取代**:无(细化 ADR-001/003 的实现层)。

## ADR-005: M2/M3/M4 实现细节:Cliopatria 疆界、事件与行迹(2026-11-18)

- **背景**:M2 需要历史疆界,M3/M4 需要事件与诗人行迹的数据建模与渲染。
- **决策**:
  1. **疆界数据源选 Cliopatria v0.0.1(Zenodo,CC-BY-4.0,49MB)** 而非 ArcGIS 对齐版 v1.1——后者仅覆盖至 1497(无清期);v0.0.1 有全年份(清快照取 1778)。数据缓存 `data/_downloaded/` 不入库,`ht import-cliopatria` 提取 5 朝快照(按 dynasty 中位年)输出约 1MB `boundaries.json`。精度定位为**示意参考层**:单一来源未逐条考据,web 淡彩+墨线且图例明示"示意·单源"(协议 G2 思想);政体名英→汉用展示层映射表。
  2. **暂不引入 PMTiles**:5 朝快照按朝代切 GeoJSON source 完全够用;规模增大后迁移(OT-006)。幽灵边界 = 前一朝代快照淡虚线层。
  3. **事件建模**:events.json(编辑索引:name/summary/type)+ 每事件一条 `occurred_at` claim(object 带 lng/lat,attestation 双源;编年体《资治通鉴》作时间优先来源)。
  4. **诗人行迹**:person_at claims(6 诗人 35 站),置信度按 attestation 数自动定档——**考据性站点(如李杜相逢、陆游生于淮上)只有单源旁证,诚实降为 G2**,不虚报 G3。作品(works.json)20 首公有领域名作带通行系年与依据说明,系年 claim 化留 M5(OT-007)。
  5. claims 文件名前缀放宽:事件 claims 用 `evt_*`,loader 同时读取 `clm_*` 与 `evt_*`(schema id pattern 同步放宽)。
  6. 行迹渲染 = GeoJSON LineString 淡金虚线 + HTML 站点标记,**随时间轴渐显(year≤当前)**,播放 = 定时推进 state.year 并逐站弹作品墨笺(同屏单气泡)。
- **备选**:自绘疆界(不可编造地理数据);CBDB 行迹(RESTRICTED,不可分发);全量 chinese-poetry 接入(227MB,暂只需名篇)。
- **影响**:pipelines(cliopatria.py/build.py)、web(stage/panel/main)、data(schema/loader 边界)。
- **维护与退出**:Cliopatria 许可署名已入 registry 与 boundaries.meta;版本升级重跑 import 即可。
- **取代**:无(细化 ADR-001)。
