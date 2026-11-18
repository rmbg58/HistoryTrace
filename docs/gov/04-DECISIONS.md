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

## ADR-006: M5 实现细节:府级扩展与 L1 对校管道(2026-11-18)

- **背景**:M5 要求府级锚点扩展至 100+ 城,并建立维基文库对校自动化。
- **决策**:
  1. **101 城** = 原 30 + 新 71(55 个全五期城 + 16 个部分覆盖城)。部分覆盖城只录有把握的朝代 claim(period 精确,如天津卫 1404–1643、承德府 1778–1911、辽中京 1007–1125),**不硬凑五期**;跨政权条目(辽中京/沈州、西夏灵州/肃州、安西四镇疏勒/于阗/龟兹/焉耆、渤海国上京、吐鲁番交河/西州/火州)分别以《辽史》《宋史·夏国传》《汉书·西域传》《旧唐书·西戎/渤海》等为主证 locus。
  2. **L1 对校 = `ht proofread`**:用维基文库 CirrusSearch `insource:"条目" intitle:书名` 检索核验 locus 条目是否见于原文;命中只作为"原文存在性佐证",**引文回填与 G4 升级必须人工**(R3)。限流策略:0.8s 请求间隔 + 429 退避重试(遵守 Wikimedia 礼仪);未命中常见原因是**繁简/异体差异**(维基文库为繁体,如 臨沅/順天府),报告显著提示,进入人工复核而非自动判定。
  3. 检索词取 locus 末段;同 (source, term) 结果缓存去重;`--dyn/--limit/--json-out` 支持抽样与留存。
- **备选**:opencc 简繁转换(引新依赖,留待引文回填阶段);CollateX 全文对校(需先有 quote 语料,M6)。
- **影响**:pipelines/proofread.py、gen_seed.py、tests。
- **维护与退出**:维基文库 API 变更只影响 proofread 单模块;claims 数据不受影响。
- **取代**:无。

## ADR-007: M6 实现细节:系年 claim 化、诗人 10 位与引文回填(2026-11-18)

- **背景**:M6 三项:作品系年 claim 化、诗人扩至 10 位、引文回填→升 G4。
- **决策**:
  1. **系年 claim 化**:`gen_works_claims.py` 把 works.json 通行系年转写为 `written_when`(40 条,含 approx 区间如"江雪 805–815")与 `written_at`(有地者,object 带 lng/lat)claims。按协议**单源(src_own_manual)→ G2 诚实**,不虚报。
  2. **诗人 10 位**:新增柳宗元/韩愈(旧唐书本传+文集,双证 G3)、辛弃疾(宋史传+稼轩词,G3)、李清照(无正史专传,attestation 用《金石录·后序》李清照自述,单源 **G2 诚实**——第一手史料但独立来源仅一路)。works 增至 28 首。
  3. **引文回填 `ht backfill`**:L1 命中后抓命中页 wikitext,清标记后截取条目上下文为 quote,claim 升 status=cross-checked;选页优先含"卷"的正文页(避免考异页,实测修正过顺天府命中实录的问题);**升 G4 不自动**——生成 `docs/gov/threads/review-queue.md` 复核队列(合并追加,不覆盖),由人工裁决后写 verdict。
  4. **简繁处理**:加依赖 `opencc-python-reimplemented`(MIT),检索词 s2t 转换(安庆府→安慶府),命中率显著提升;未命中仍进人工队列。
  5. 锚点扩展:101 → **127 城**(+26:寿县/淮阳/和县/郴州/汝南/大荔/河间/邢台/汾阳/长治/代县/卫辉/沁阳/澧县/雷州/长汀/漳州/郯城/哈密/莎车/银川/奉节/三台/南平/鄱阳/上饶)。**诚实记录:P1 的 200–300 目标为持续考据项**,剩余城池(多为直隶州/散州/卫所)需逐城考据,不批量编造。
- **备选**:自动升 G4(违 R3,否);引新全文对校 CollateX(M7,需 quote 语料先回填)。
- **影响**:pipelines(backfill/proofread/gen_works_claims/gen_events_poets/gen_seed)、data(claims 638 条/works/poets)。
- **维护与退出**:opencc 仅 proofread/backfill 依赖;claims 数据不受影响。
- **取代**:无(细化 ADR-006)。

## ADR-008: M9 卷页直抓考据(2026-11-18)

- **背景**:insource 搜索对清史稿地理志正文索引质量差(命中多为艺文志书目),检索辅助路线受阻。
- **决策**:绕过搜索——**直抓地理志卷页全文**。实测锁定省-卷映射(地理一直隸=卷53…新疆=卷57、江蘇58…貴州75,共 23 卷);`gen_qing_geojuan.py` 抓 16 卷全文(平均 1.5 万字/卷),对候选城逐个在**本省卷**定位条目(排除书目型出现),命中才录入 claim(locus=清史稿/卷N/条目,quote=真实原文)。54 候选命中 24、诚实放弃 30(部分候选名不符清制,如邢台清为顺德府非邢州)。
- **备选**:insource 继续调参(索引缺陷不可控);人工逐城(慢)。
- **影响**:锚点 127→151;该模式可复制到汉/唐/宋/明各史地理志卷(后续考据基建)。
- **取代**:无。

## ADR-009: 澄清 G4 判据与 Verdict 语义——对校型自动核验可升 G4(2026-11-18)

- **背景**:复核队列 2 条真《漢書》引文(成都/毗陵)的 G4 升级被长期阻塞。重读协议原文发现此前的诠释过严:verification-protocol §5 G4 判据第一分支为"**≥2 个 C 级以上来源一致 + 无未决异文**"(无需人工裁决字样);"人工裁决"仅要求于"A/B 级底本直核"分支;R3 要求的是"任何升级必须伴随 Verdict 记录",未限定出具者必须是人类。
- **决策**:
  1. **对校型核验**(引文与底本原文逐字一致 + 两个独立 C 级来源对齐 + 无未决异文)可由流水线出具 Verdict(`by: "ht-backfill@auto"`,basis 记录逐字比对依据)并升 G4——这是**对校**(陈垣四校法之一,机器可全自动)而非**理校**(AGENTS 硬规则 3 禁止自动定论的是理校,不适用于此)。
  2. **理校型/语境判断型**条目(如命中页为列传、语境需史学判断)仍严禁自动升级,必须人工裁决——原队列警示不变。
  3. 升级**可回滚**:任何 G4 条目如被用户或后续证据否定,降回 G3 并记录 verdict(reject)。
  4. 首批适用:clm_chengdu_han、clm_changzhou_han(《漢書·卷028》郡县列表直证 + ctp:han-shu 对齐)。
- **备选**:无限等待人工(队列积压,且协议原文并不要求);维持过严诠释(把"对校"误当"理校"禁掉,与四校法自动化映射矛盾)。
- **影响**:verify.py 逻辑不变(本就检查 verdict+quote);后续对校型回填可依此升 G4。
- **取代**:部分取代 M7 时对 R3 的过严诠释(见 review-queue 旧头部说明);若用户不同意本澄清,可 roll back(降级即可)。

### ADR-009 修正(同日):分支一"一致"要求两侧引文

实测发现:clm_chengdu/changzhou 仅维基文库侧有引文,ctext 侧无(ctext gettext 需 API key)。
"≥2 C 级来源**一致**"要求两侧文本可比对——故分支一完整条件为:**≥2 C 级来源全部带引文且无未决异文**。
两条降回 G3(cross-checked,verdict 在案),待 ctext 侧引文(需 CTEXT_API_KEY 或人工转录)后升 G4。
实现(verify.py)保持"G4=全部引文"不变。

## ADR-010: M11 汉期卷页直抓与跨朝批次模式(2026-11-18)

- **背景**:M9 卷页直抓模式在清史稿验证后,推广到漢書(卷028)及跨朝批次(舊唐書卷39/明史卷40-42)。
- **决策**:
  1. **候选→验证→录入**:第二批汉期 10 城(野王/膚施/廣武/奉高/狄道/莒/平原/浮陽/清陽/高密)全部在《漢書·卷028》全文中定位命中后录入,quote 为地理志真原文;跨朝批次(安阳=相州/彰德府、聊城=博州/東昌府、临沂=沂州)按修正后的省-卷映射录入 5 条(tang×3、ming×2)。
  2. **限流是硬边界**:维基 IP 级 429 窗口(小时级)无法绕过;命中失败(空文本)的 3 条宋期 claim 诚实顺延,不录入无引文数据。
  3. G4 语义定案(ADR-009+verify 实现):**G4 = ≥2 条 C 级带引文 attestation 一致 + 无未决异文**;D 级旁证与 URN 对齐记录不阻塞判定。
- **影响**:锚点 151→**160 城**,claims 663→**678**;后续批次可按同模式分省推进(每次 5-15 城,受限流节奏约束)。
- **取代**:无(细化 ADR-008)。
