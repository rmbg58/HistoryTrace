# 进度账本(STATE)

> 由会话协议维护。行数预算来自 manifest;详细证据、历史和长任务说明归档到 `threads/` 或 evidence 文件。

Updated: 2026-11-18 | Last audited commit: M2/M3/M4 开发提交(2026-11-18) | 阶段: MVP 功能层完成 | 当前里程碑: M5 数据深化

## 在途任务(领取即租约)

| ID | 任务 | Owner | 基线/范围 | 状态 | 更新于 | 证据/下一步 |
|----|------|-------|-----------|------|--------|------------|
| T-001 | 初始化治理体系(devinit standard) | agent | 全仓库 docs/gov + manifest + AGENTS.md | done | 2026-11-18 | 治理文件全套 + LICENSE/MIT + DATA-LICENSE;首次基线提交即证据 |
| T-002 | M1 全面开发:数据层+pipelines+种子数据+web 古风 UI | agent | data/ pipelines/ web/ 全部 | done | 2026-11-18 | 全量验证通过(见变更摘要);浏览器交互验收截图通过 |
| T-003 | M2+M3+M4:疆界图层、府级扩展、事件层、诗人足迹 | agent | data/ pipelines/ web/ | done | 2026-11-18 | 195 claims 全绿;浏览器验收:疆界/事件印章/行迹播放+作品气泡 |

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
- [ ] M5 数据深化(下一阶段)
  - [ ] 维基文库地理志批量抓取 + L1 对校自动化(引文回填,升 G4)
  - [ ] 作品系年 claim 化(written_at/when,引编年笺注为 attestation)
  - [ ] 府级锚点扩展至 100+;R4 来源更新回归自动化

## Open Threads(发现即记录)

| ID | 类型 | 描述 | 优先级 |
|----|------|------|--------|
| OT-001 | question | 静态站部署目标(GitHub Pages / Cloudflare Pages)未定;CI 中 R1 自动校验的触发方式随之确定 | 中 |
| OT-002 | tech-debt | web 字体方案:系统字体栈起步,自托管思源宋体/楷体(OFL)待性能评估后决策 | 低 |
| OT-004 | tech-debt | 主 bundle 1.1MB(maplibre 占大头):接部署时做动态 import / manualChunks 分包 | 中 |
| OT-006 | idea | PMTiles:现用按朝代 GeoJSON 快照(约 1MB)足够;锚点/几何规模增大后迁移 PMTiles + 矢量瓦片 | 低 |
| OT-007 | idea | 作品气泡与行迹站点匹配目前按坐标距离;将 works 挂 claim 后改用 claim 关联 | 低 |

已关闭:OT-003(验证命令回填);OT-005(疆界图层已接,Cliopatria 墨线+幽灵边界)。

类型:bug / tech-debt / idea / question / reuse / governance。关闭后移入 `threads/archive.md`。

## 变更摘要(按任务/阶段聚合;更早的移入 threads/log.md)

| 日期 | 摘要 | 相关模块 | commit 范围/证据 |
|------|------|----------|------------------|
| 2026-11-18 | M2/M3/M4:ht import-cliopatria(Zenodo CC-BY-4.0 → 5 朝疆界快照,墨线+幽灵边界+图例);府级扩展 30 城 150 claims;事件层(10 史事 claims + events.json + 朱印落点 + 事件面板);诗人足迹(6 诗人 35 站 person_at claims + 20 首名作 + 行迹线随时间轴渐显 + 播放 + 作品墨笺气泡);修复 loader evt_ glob/schema id/衔接年重叠;185→195 claims 全绿;浏览器验收疆界/事件/行迹播放 | data, pipelines, web | M2M3M4 开发提交 |
| 2026-11-18 | M1 全面开发:JSON Schema×2 + 来源注册×12 + 白名单;`ht` CLI(verify/build/report/era/import-wikisource);种子 50 claims(10 城×5 朝,每条 2 来源,G3);web 古风 UI(宣纸/墨/朱砂,时间轴+地图 markers+沿革卡+佐证笺注);pytest 9 通过、ruff 0 问题、vitest 6 通过、typecheck/build 通过;浏览器验收(朝代切换名称联动/佐证展开/都城朱砂标记) | data, pipelines, web | M1 开发提交 |
| 2026-11-18 | 完成三路调研与总体规划(docs/research + project-plan + verification-protocol) | docs | 见文档内来源链接 |
| 2026-11-18 | 初始化治理体系(devinit standard):manifest、docs/gov 全套、AGENTS.md、LICENSE(MIT)+ DATA-LICENSE(CC BY-SA 4.0) | docs/gov, AGENTS.md | 首次基线提交 |
