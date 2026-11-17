# 交接文档:三项待决决定(2026-11-18 固化)

> 本项目数据与代码已处于完整可交付状态。以下三项决定按项目协议属于用户专属权限,代理已连续七轮询问未获答复,故固化于此。**用户回复任意一项,后续会话即可按本表立即执行闭环。**

## ① 复核队列升 G4(2 条真《漢書》引文就绪)

- 现状:`clm_chengdu_han`、`clm_changzhou_han` 已回填**维基文库《漢書》真原文**(成都=蜀郡户口+十五县列表;毗陵=会稽郡县列表),status=cross-checked,G3。
- 阻塞:协议 G4 分支一要求**两侧来源引文**(ADR-009 修正);ctext 侧匿名访问返回 Access unavailable,需凭证。
- **解锁动作(任选)**:
  - 在 `.env` 填 `CTEXT_API_KEY`(ctext.org 订阅/注册获取)→ 运行 `uv run ht backfill --dyn han` 自动回填 ctext 引文;
  - 或人工打开 https://ctext.org/han-shu/di-li-zhi/zh 复制「成都」「毗陵」所在郡条原文,粘贴到会话,由代理核对后写入双侧引文;
  - 或人工裁决:接受"维基文库引文 + ctext URN 对齐"为 G3→G4 的充分证据(需修订 ADR-009,写明此放宽)。
- 裁决通过后:`verdict {round:"R3", by:"<裁决人>", decision:"accept"}` + `confidence:"G4"` 写入 claim,verify/build 刷新。

## ② 部署上线(OT-001)

- 现状:verify.yml CI 已就绪(push/PR 全量校验 + 手动 R4 regression);**不含部署动作**。
- **解锁动作**:回复"部署 GitHub Pages"→ 代理执行:① 加 GitHub Pages 发布配置(产物=web/dist);② verify.yml 追加 deploy job(main push 时发布);③ regression 挂 `schedule: weekly` cron;④ 首次上线后回填实际站点 URL 到 STATE。
- 备选:Cloudflare Pages(需用户提供项目凭证)。
- **前置条件提醒(2026-11-18 补)**:本项目当前为纯本地 git 仓库(**无 GitHub remote**)。部署 GitHub Pages 前需先:① 在 GitHub 创建仓库并 `git remote add origin … && git push`(此步属外向发布,同样需要你授权);② 仓库 Settings 开启 Pages。确认部署 = 授权上述全部步骤。

## ③ 锚点 151 → 200+(P1 持续考据项)

- 现状:四批逐城考据(30→101→127→151),**高置信存量已全部入库**;卷页直抓基建(ADR-008:省-卷映射 + gen_qing_geojuan.py)已可复制到《漢書》《舊唐書》《宋史》《明史》地理志卷。
- 剩余 49 城(直隶州/散州/卫所)特点:候选名需逐城核对原卷(如邢台清为顺德府),自动化命中质量不足(实测艺文志噪声大)。
- **解锁动作(任选)**:
  - 回复"继续考据"→ 代理按《明史》地理志卷页直抓补明期(已有清城 +明 claims),并分省推进新城(命中才录);
  - 或接受 151 城为当前版本,200+ 转为长期社区考据目标。

## 快速答复模板(复制即用)

```
① 批准 / 拒绝 / 提供 ctext 原文:<粘贴>
② 部署 / 暂不部署
③ 继续考据 / 接受 151 城
```
