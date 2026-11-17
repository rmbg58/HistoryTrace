# 进度账本(STATE)

> 由会话协议维护。行数预算来自 manifest;详细证据、历史和长任务说明归档到 `threads/` 或 evidence 文件。

Updated: 2026-11-18 | Last audited commit: M1 开发提交(2026-11-18) | 阶段: P0 完成 → P1 就绪 | 当前里程碑: M2 MVP 地图(边界瓦片接入)

## 在途任务(领取即租约)

| ID | 任务 | Owner | 基线/范围 | 状态 | 更新于 | 证据/下一步 |
|----|------|-------|-----------|------|--------|------------|
| T-001 | 初始化治理体系(devinit standard) | agent | 全仓库 docs/gov + manifest + AGENTS.md | done | 2026-11-18 | 治理文件全套 + LICENSE/MIT + DATA-LICENSE;首次基线提交即证据 |
| T-002 | M1 全面开发:数据层+pipelines+种子数据+web 古风 UI | agent | data/ pipelines/ web/ 全部 | done | 2026-11-18 | 全量验证通过(见变更摘要);浏览器交互验收截图通过 |

状态:planned / in_progress / blocked / waiting_external / done / abandoned。超时只标记需确认,不自动放弃;任务必须保留下一步或关闭原因。

## 里程碑

- [x] M1 脚手架 + 种子数据全流程 — 验收:`uv run ht verify` 通过(50 claims,0 错误);`pnpm build` 通过;浏览器交互验收通过
  - [x] Vite + 原生 TS 脚手架(web/),MapLibre + 古风 tokens 接入
  - [x] `ht` CLI(pipelines/):verify(R0 许可白名单+schema / R1 一致性)/ build / report / era / import-wikisource
  - [x] Claim/Source JSON Schema(2020-12)+ 12 个来源注册
  - [x] 种子数据:10 锚点城市 × 5 朝代 = 50 claims,每条 2 来源,全部 G3
- [ ] M2 MVP 地图 — 验收:朝代切换 <100ms;边界快照(PMTiles)接入;溯源面板完整
  - [ ] Cliopatria 中国几何提取 → PMTiles;政区填充与幽灵边界
  - [ ] 维基文库地理志批量对校(L1)扩展府级地名
- [ ] M3 事件层 / M4 诗人足迹(见 docs/project-plan.md 路线图)

## Open Threads(发现即记录)

| ID | 类型 | 描述 | 优先级 |
|----|------|------|--------|
| OT-001 | question | 静态站部署目标(GitHub Pages / Cloudflare Pages)未定;CI 中 R1 自动校验的触发方式随之确定 | 中 |
| OT-002 | tech-debt | web 字体方案:系统字体栈起步,自托管思源宋体/楷体(OFL)待性能评估后决策 | 低 |
| OT-004 | tech-debt | 主 bundle 1.06MB(maplibre 占大头):P1 接边界时做动态 import / manualChunks 分包 | 中 |
| OT-005 | idea | 地图暂无海岸线/疆界底图,纯宣纸+点标记;M2 接 Cliopatria 几何后补"墨线疆界"层 | 中 |

已关闭:OT-003(验证命令已回填 manifest.validation 并实测通过)。

类型:bug / tech-debt / idea / question / reuse / governance。关闭后移入 `threads/archive.md`。

## 变更摘要(按任务/阶段聚合;更早的移入 threads/log.md)

| 日期 | 摘要 | 相关模块 | commit 范围/证据 |
|------|------|----------|------------------|
| 2026-11-18 | M1 全面开发:JSON Schema×2 + 来源注册×12 + 白名单;`ht` CLI(verify/build/report/era/import-wikisource);种子 50 claims(10 城×5 朝,每条 2 来源,G3);web 古风 UI(宣纸/墨/朱砂,时间轴+地图 markers+沿革卡+佐证笺注);pytest 9 通过、ruff 0 问题、vitest 6 通过、typecheck/build 通过;浏览器验收(朝代切换名称联动/佐证展开/都城朱砂标记) | data, pipelines, web | M1 开发提交 |
| 2026-11-18 | 完成三路调研与总体规划(docs/research + project-plan + verification-protocol) | docs | 见文档内来源链接 |
| 2026-11-18 | 初始化治理体系(devinit standard):manifest、docs/gov 全套、AGENTS.md、LICENSE(MIT)+ DATA-LICENSE(CC BY-SA 4.0) | docs/gov, AGENTS.md | 首次基线提交 |
