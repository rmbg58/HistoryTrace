# 模块注册表

> 改模块前必读其条目。新增/删除/重命名模块必须同步更新本表(会话协议第 4 条)。

| 模块 | pathKind | 路径/ownership | 职责 | 允许依赖 | 禁改/禁区 | 状态 |
|------|----------|---------------|------|----------|-----------|------|
| web | planned | web/ | 前端静态站:MapLibre 地图、朝代/年份时间轴、沿革卡片、溯源面板 | 构建产物(public/data)、MapLibre、PMTiles | 不直接读 data/claims;不引入 UI 组件库;不内嵌密钥 | 规划中 |
| pipelines | planned | pipelines/ | `ht` CLI:import(来源→claim)、verify(R0–R2 机器校验)、build(产物生成)、report(质量报告) | data/claims、data/registry、已批第三方(geopandas/shapely 等,记 ADR) | 不 import web;不写仓库外文件(除 _downloaded 缓存);校验四铁律不可绕过 | 规划中 |
| claims | planned | data/claims/**(clm_*.json) | 声明库:唯一事实源,git 版本化,每条带 attestations/verdicts/confidence | — | 只经 pipelines 或 git PR 修改;禁止手工批量重写 | 规划中 |
| registry | planned | data/registry/**(src_*.json + whitelist) | Source 注册表:来源分级(A–E)、许可白名单、获取方式 | — | 白名单变更必须走 ADR(涉及法律风险) | 规划中 |
| assets-in | generated(外部) | data/_downloaded/(gitignore) | 外部来源下载缓存(CHGIS/CBDB/维基文库 dump 等) | — | 永不入库;重建可由 pipelines 脚本完成 | 规划中 |
| docs-gov | active | docs/gov/ | 治理事实源(manifest 指向) | — | append-only 规则见 04-DECISIONS.md | 稳定 |
| docs-domain | active | docs/(project-plan.md、verification-protocol.md、research/) | 领域规划、校验协议、调研报告 | — | 调研报告为快照,不随代码改写;协议修订走 ADR | 稳定 |

pathKind:active / planned / generated / external / deprecated。状态取值:规划中 / 开发中 / 稳定 / 维护模式 / 废弃。

> sync 审计将本表与实际路径、包、服务或 ownership glob 对比:active 目标消失或新增实际依赖才报告漂移;planned 目标不存在不视为废弃。
