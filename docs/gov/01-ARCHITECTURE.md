# 架构

> 改架构、跨模块、新增模块前必读。修改本文档须 append ADR 到 04-DECISIONS.md。
> 领域协议(校验机制)的完整定义在 `docs/verification-protocol.md`,本文只记录工程结构与边界。

## 分层与依赖方向

```
web/(前端,只读产物)
   │ 读取
   ▼
public/data 或 web/public/data(构建产物:沿革索引 / PMTiles / 实体 JSON)
   ▲ 生成
   │
pipelines/(ht CLI:import → verify → build)      data/claims/(声明库,git 版本化)
   │ 读写                                              ▲
   └───────────────────────────────────────────────────┘
data/registry/(Source 注册表+许可白名单)──▶ pipelines 读取
```

依赖规则:web 不读 `data/claims`(只读构建产物);pipelines 不 import web;`data/claims` 与 `data/registry` 只经 pipelines 程序化修改(人工修订走 git PR);外部来源下载缓存(`data/_downloaded/`,gitignore)不进入仓库。

## 数据流

外部来源(维基文库 API / ctext 点查 / WHG / Cliopatria / GeoNames / 人工录入)→ `ht import-*` 抽取为 Claim(带 Attestation)→ `ht verify` 依 verification-protocol 跑 R0(许可/schema)→ R1(对校/本校,机器置信分)→ PR 人工复核(R2/R3)→ `ht build` 派生静态产物(沿革索引、PMTiles、实体 JSON)→ web 静态站按年份/朝代加载快照渲染。

## 模块边界

模块的唯一注册表是 `03-MODULES.md`。新增模块必须先在那里登记(职责、允许依赖、禁区),再写代码。

## 安全与信任边界

- 输入校验位置:`ht` CLI 各子命令入口统一 JSON Schema 校验(claims/registry);web 无用户输入(纯展示)
- 密钥/敏感配置:只允许出现在 `.env`(pipelines 运行时);当前仅 `CTEXT_API_KEY`(可选)。禁止写入代码、文档、产物
- 服务端/数据库授权:不适用(无后端无数据库);README/卡片展示的引文必须可溯源(非授权问题,是数据诚信问题,由校验协议约束)
- 浏览器直访存储:不适用
- 多用户验收:不适用

## 外部服务与退出边界

| 服务 | 用途/数据 | 调用边界 | 导出/替换方式 | 失败行为 |
|------|-----------|----------|----------------|----------|
| ctext.org API | 古籍引文点查核对(URN 溯源) | 低频、匿名或 env key;禁止批量抓取 | 引文落库后不依赖线上;可换维基文库同文核对 | 该来源缺失 → claim 降为单源 G2,不阻塞流水线 |
| Wikimedia API | 廿四史全文批量 | 遵守 API 礼仪(UA/串行/限速) | dump 全量可离线 | 同上 |
| 静态托管(平台待定,OT-001) | 发布 web 产物 | 只读静态文件 | 产物可部署任意静态平台 | 不影响数据层 |

核心业务规则位于 `pipelines/`(校验协议实现),不散落在 web 组件或外部服务中。只为 ctext 这类高退出成本边界保留薄适配(source registry 已是天然适配层)。
