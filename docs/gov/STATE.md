# 进度账本(STATE)

> 由会话协议维护。行数预算来自 manifest;详细证据、历史和长任务说明归档到 `threads/` 或 evidence 文件。

Updated: 2026-11-18 | Last audited commit: 首次基线提交(2026-11-18) | 阶段: P0 基础设施 | 当前里程碑: M1 脚手架 + 种子 claims 走通 R0–R1

## 在途任务(领取即租约)

| ID | 任务 | Owner | 基线/范围 | 状态 | 更新于 | 证据/下一步 |
|----|------|-------|-----------|------|--------|------------|
| T-001 | 初始化治理体系(devinit standard) | agent | 全仓库 docs/gov + manifest + AGENTS.md | done | 2026-11-18 | 治理文件全套 + LICENSE/MIT + DATA-LICENSE;首次基线提交即证据 |

状态:planned / in_progress / blocked / waiting_external / done / abandoned。超时只标记需确认,不自动放弃;任务必须保留下一步或关闭原因。

## 里程碑

- [ ] M1 脚手架 + 种子数据全流程 — 验收:`uv run ht verify` 对种子集输出 R0/R1 报告;`pnpm -C web build` 通过
  - [ ] Vite + 原生 TS 脚手架(web/),MapLibre + 古风 tokens 接入
  - [ ] `ht` CLI 骨架(pipelines/):`import-wikisource` / `verify`(R0 许可白名单 + schema)
  - [ ] Claim/Source JSON Schema 定义
  - [ ] 种子数据:10 锚点城市 × 5 朝代(汉/唐/宋/明/清),每条 ≥2 来源
- [ ] M2 MVP 地图 — 验收:朝代切换 <100ms;种子地点沿革卡片可展开溯源
- [ ] M3 事件层 / M4 诗人足迹(见 docs/project-plan.md 路线图)

## Open Threads(发现即记录)

| ID | 类型 | 描述 | 优先级 |
|----|------|------|--------|
| OT-001 | question | 静态站部署目标(GitHub Pages / Cloudflare Pages)未定;CI 中 R1 自动校验的触发方式随之确定 | 中 |
| OT-002 | tech-debt | web 字体方案:系统字体栈起步,自托管思源宋体/楷体(OFL)待性能评估后决策 | 低 |
| OT-003 | governance | 验证命令均为 planned/unverified,脚手架落地后回填 manifest.validation 并复核 | 高 |

类型:bug / tech-debt / idea / question / reuse / governance。关闭后移入 `threads/archive.md`。

## 变更摘要(按任务/阶段聚合;更早的移入 threads/log.md)

| 日期 | 摘要 | 相关模块 | commit 范围/证据 |
|------|------|----------|------------------|
| 2026-11-18 | 完成三路调研与总体规划(docs/research + project-plan + verification-protocol) | docs | 见文档内来源链接 |
| 2026-11-18 | 初始化治理体系(devinit standard):manifest、docs/gov 全套、AGENTS.md、LICENSE(MIT)+ DATA-LICENSE(CC BY-SA 4.0) | docs/gov, AGENTS.md | 首次基线提交 |
