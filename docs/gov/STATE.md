# 进度账本(STATE)

> 由会话协议维护。行数预算来自 manifest;详细证据、历史和长任务说明归档到 `threads/` 或 evidence 文件。

Updated: 2026-11-18 | Last audited commit: M9 提交(2026-11-18) | 阶段: 151 城卷页考据落地 | 当前里程碑: M10(裁决 G4、部署、剩余 49 城考据)

## 在途任务(领取即租约)

| ID | 任务 | Owner | 基线/范围 | 状态 | 更新于 | 证据/下一步 |
|----|------|-------|-----------|------|--------|------------|
| T-001 | 初始化治理体系(devinit standard) | agent | 全仓库 docs/gov + manifest + AGENTS.md | done | 2026-11-18 | 治理文件全套;首次基线提交 |
| T-002 | M1 全面开发 | agent | data/ pipelines/ web/ | done | 2026-11-18 | 全量验证;浏览器验收 |
| T-003 | M2+M3+M4:疆界/事件/诗人足迹 | agent | data/ pipelines/ web/ | done | 2026-11-18 | 195 claims 全绿;浏览器逐层验收 |
| T-004 | M5:府级扩展 101 城 + L1 对校管道 | agent | data/ pipelines/ | done | 2026-11-18 | 498 claims 全绿;proofread 实测命中 |
| T-005 | M6:系年 claim 化 + 诗人 10 位 + 引文回填管道 + 锚点 127 | agent | data/ pipelines/ web/ | done | 2026-11-18 | 638 claims 全绿;**复核队列待用户裁决升 G4**(docs/gov/threads/review-queue.md,4 条已回填真实引文) |
| T-006 | M7:无效引文回滚重考 + R4 回归自动化 + 部署方案记录 | agent | data/ pipelines/ | done | 2026-11-18 | 回滚 2 条误中→卷页优先重考;`ht regression` 9/9 稳定;verify.yml CI 已建(校验,不含部署) |
| T-007 | M8:引文搜索缺陷修复+队列重考 | agent | data/ pipelines/ | done | 2026-11-18 | 旧 10 条作废清除;过滤修复后重考 8 条;**队列 8 条待用户裁决升 G4** |
| T-008 | M8:verify.yml CI 建立(校验,不含部署;OT-001 待用户确认) | agent | .github/ | done | 2026-11-18 | workflow_dispatch 可手动跑 R4 regression |
| T-009 | M9:卷页直抓考据(清史稿地理志卷 53-75 定位)+24 城 | agent | data/ pipelines/ | done | 2026-11-18 | 省-卷映射实测(直隶53…贵州75);24 城带真源 quote 录入;151 城 663 claims 全绿;剩余 49 城待证据(部分候选名不符清制) |

状态:planned / in_progress / blocked / waiting_external / done / abandoned。超时只标记需确认,不自动放弃;任务必须保留下一步或关闭原因。

## 里程碑

- [x] M1 脚手架 + 种子数据全流程 — 验收:`uv run ht verify` 通过(50 claims,0 错误);`pnpm build` 通过;浏览器交互验收通过
  - [x] Vite + 原生 TS 脚手架(web/),MapLibre + 古风 tokens 接入
  - [x] `ht` CLI(pipelines/):verify(R0 许可白名单+schema / R1 一致性)/ build / report / era / import-wikisource
  - [x] Claim/Source JSON Schema(2020-12)+ 12 个来源注册
  - [x] 种子数据:10 锚点城市 × 5 朝代 = 50 claims,每条 2 来源,全部 G3
- [ ] M2 MVP 地图 — 验收:Cliopatria 疆界快照(5 朝)接入,墨线+淡彩+前朝幽灵边界;30 城府级沿革;图例标注"示意单源"
  - [x] `ht import-cliopatria`:Zenodo v0.0.1(CC-BY-4.0)→ 朝代快照 GeoJSON(约 1MB)
  - [x] 府级地名扩展:10 → 30 城(含河西走廊/幽燕/江南),150 条名称 claims
  - [ ] 维基文库地理志批量对校(L1)与引文回填(→ M5)
- [x] M3 事件层 — 验收:10 大史事 claims(秦统一→鸦片战争),地图朱印落点 + 事件面板 + 当朝高亮/他朝淡化
- [x] M4 诗人足迹 — 验收:6 诗人 35 站行迹 claims,淡金行迹随时间轴渐显 + 播放动画 + 作品墨笺气泡(20 首名作带通行系年)
- [x] M5 数据深化
  - [x] 府级锚点扩展 30 → 101 城(498 claims 全绿)
  - [x] L1 对校管道 `ht proofread`(insource 核验 + 限流退避 + 繁简提示)
- [x] M6 对校闭环与规模扩展
  - [x] **作品系年 claim 化**:40 条 written_when/written_at(单源 G2 诚实;approx 区间如"江雪 805–815")
  - [x] **诗人扩至 10 位**:+柳宗元/韩愈/辛弃疾(双证 G3)+李清照(金石录后序自述,单源 G2 诚实),works 28 首
  - [x] **引文回填管道** `ht backfill`:抓命中页真实原文回填 quote(选页优先卷页),status 升 cross-checked,**复核队列** `docs/gov/threads/review-queue.md` 待人工裁决升 G4(R3:机器/代理不得代替)
  - [x] 锚点 101 → **127 城**(+26:寿县/淮阳/郴州/汝南/河间/邢台/汾阳/长治/卫辉/沁阳/雷州/长汀/漳州/哈密/莎车/银川兴庆府/奉节/三台/南平/鄱阳/上饶 等)
  - [ ] 人工裁决复核队列 → 升 G4(**8 条已回填待裁决**,其中 2 条为确证真《漢書》地理志原文;搜索缺陷已修:书名前缀过滤)
  - [x] 锚点 127 → **151 城**(+24:清直隶州/府卷页直抓,真源 quote 录入——光州/汝州/泰安/沂州/曹州/武定/沁州/保德/解州/霍州/隰州/邠州/乾州/鄜州/茂州/忠州/思南/石阡/黎平/大方/福泉/靖州/道州/南通)
  - [ ] 锚点 151 → 200+(P1 持续考据项:剩 49 城,部分候选名不符清制,需逐城人工核对清史稿原卷)
  - [x] **R4 来源更新回归自动化**:`ht regression`(cross-checked 引文重检,实测 9/9 稳定);CI 触发待部署(OT-001)
  - [ ] 部署上线(OT-001 方案与推荐已记录,待用户确认)

## Open Threads(发现即记录)

| ID | 类型 | 描述 | 优先级 |
|----|------|------|--------|
| OT-001 | question | 部署目标待用户确认(推荐 GitHub Pages;备选 Cloudflare)。已建 verify.yml CI(校验+手动 regression,不含部署动作);确认后只需加 Pages 配置 | 中 |
| OT-002 | tech-debt | web 字体方案:系统字体栈起步,自托管思源宋体/楷体(OFL)待性能评估后决策 | 低 |
| OT-004 | tech-debt | 主 bundle 1.1MB(maplibre 占大头):接部署时做动态 import / manualChunks 分包 | 中 |
| OT-006 | idea | PMTiles:现用按朝代 GeoJSON 快照(约 1MB)足够;锚点/几何规模增大后迁移 PMTiles + 矢量瓦片 | 低 |
| OT-007 | idea | 作品气泡与行迹站点匹配目前按坐标距离;将 works 挂 claim 后改用 claim 关联 | 低 |

已关闭:OT-003(验证命令回填);OT-005(疆界图层已接,Cliopatria 墨线+幽灵边界)。

类型:bug / tech-debt / idea / question / reuse / governance。关闭后移入 `threads/archive.md`。

## 变更摘要(按任务/阶段聚合;更早的移入 threads/log.md)

| 日期 | 摘要 | 相关模块 | commit 范围/证据 |
|------|------|----------|------------------|
| 2026-11-18 | M9:卷页直抓考据——清史稿地理志省-卷映射实测锁定(直隸53…貴州75,新疆57);gen_qing_geojuan.py 直抓 16 卷全文定位 54 候选,24 城命中录入(quote=地理志真原文);31 未命中诚实放弃(部分候选名不符清制);151 城 663 claims 全绿 | data, pipelines | M9 提交 |
| 2026-11-18 | M8:引文搜索缺陷修复——`intitle:漢書` 子串误匹配後漢書/南明史稿/宋史紀事本末等(10 条旧引文全部作废清除);parse_search_response 加书名前缀过滤,重考后队列 8 条(含真《漢書·卷028》地理志原文 2 条:成都/毗陵);verify.yml CI 建立(push/PR 全量校验+手动 R4 regression,不含部署);OT-001 部署推荐记录待用户确认 | data, pipelines, .github | M8 提交 |
| 2026-11-18 | M7:无效引文回滚重考(常德府艺文志页/顺天府吴晗论文页 2 条 reject→卷页优先重回填);`ht regression` R4 回归命令(cross-checked 引文重检+regex 修复页名内嵌括号,实测 9/9 稳定);银川+明宁夏镇;gen_seed 重跑保留已回填 quote(修复覆盖冲突);OT-001 部署推荐记录 | data, pipelines, docs | M7 提交 |
| 2026-11-18 | M6:作品系年 claim 化(40 条 written_when/at,G2 诚实);诗人 6→10 位(+柳宗元/韩愈/辛弃疾双证 G3、李清照金石录后序自述 G2),works 28 首;`ht backfill` 引文回填管道(opencc 简转繁、卷页优先、复核队列合并追加),实测回填 5 条真实引文;锚点 101→127 城(+26);638 claims verify 全绿;pytest 13;浏览器验收 10 诗人+辛弃疾行迹播放;**复核队列 4 条待用户裁决升 G4** | data, pipelines, web | M6 提交 |
| 2026-11-18 | M5:府级锚点 30→101 城(+71 城,新增 303 条名称 claims,含辽中京/西夏灵州肃州/西域安西四镇疏勒于阗龟兹焉耆/渤海国上京/吐鲁番交河等跨政权条目);`ht proofread` L1 对校管道(维基文库 insource 检索、429 退避+0.8s 间隔、繁简差异提示、--json 输出);498 claims verify 全绿;pytest 13 项;浏览器截图 101 城+清疆界 | data, pipelines | M5 提交 |
| 2026-11-18 | M2/M3/M4:ht import-cliopatria(Zenodo CC-BY-4.0 → 5 朝疆界快照,墨线+幽灵边界+图例);府级扩展 30 城 150 claims;事件层(10 史事 claims + events.json + 朱印落点 + 事件面板);诗人足迹(6 诗人 35 站 person_at claims + 20 首名作 + 行迹线随时间轴渐显 + 播放 + 作品墨笺气泡);修复 loader evt_ glob/schema id/衔接年重叠;185→195 claims 全绿;浏览器验收疆界/事件/行迹播放 | data, pipelines, web | M2M3M4 开发提交 |
| 2026-11-18 | M1 全面开发:JSON Schema×2 + 来源注册×12 + 白名单;`ht` CLI(verify/build/report/era/import-wikisource);种子 50 claims(10 城×5 朝,每条 2 来源,G3);web 古风 UI(宣纸/墨/朱砂,时间轴+地图 markers+沿革卡+佐证笺注);pytest 9 通过、ruff 0 问题、vitest 6 通过、typecheck/build 通过;浏览器验收(朝代切换名称联动/佐证展开/都城朱砂标记) | data, pipelines, web | M1 开发提交 |
| 2026-11-18 | 完成三路调研与总体规划(docs/research + project-plan + verification-protocol) | docs | 见文档内来源链接 |
| 2026-11-18 | 初始化治理体系(devinit standard):manifest、docs/gov 全套、AGENTS.md、LICENSE(MIT)+ DATA-LICENSE(CC BY-SA 4.0) | docs/gov, AGENTS.md | 首次基线提交 |
