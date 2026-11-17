# HistoryTrace

可信的中国历史时空互动平台:朝代切换疆域、点选地点看历代名称沿革,后续叠加历史事件与诗人足迹;一切数据经多来源多轮次校验(协议:`docs/verification-protocol.md`)。

> 治理文档在 `docs/gov/`。本文件只放硬规则与会话协议,细则按需读对应文档。

## 硬规则(违反即错误)

1. **数据许可红线**(ADR-002,法律风险级):发布产物只允许包含 `data/registry/` 白名单来源;CHGIS、CBDB 等受限数据只存 `data/_downloaded/`(gitignore),永不入仓库;中华书局点校本只参校不转录。白名单变更必须先追加 ADR。
2. **claims 是唯一事实源**:`data/claims/` 之外不得出现第二份"事实";`web/` 只读构建产物,不读 claims;产物必须可由 `ht build` 重建。
3. **校验四铁律**实现与执行不可绕过:每条声明必有来源;冲突不合并;机器只降级不升级;理校(LLM/规则推断)永不自动定为结论。
4. 修改接口、模块结构或新增模块,必须同步更新 `docs/gov/03-MODULES.md` 对应条目。
5. 引入新依赖、更换框架/地图引擎/外部服务必须先记录 ADR 到 `docs/gov/04-DECISIONS.md`;不自动升级整套依赖。
6. 样式只使用 `web/src/styles/tokens.css` 定义的令牌(古风体系,事实源 `docs/gov/05-DESIGN.md`);禁止引入 UI 组件库与第三方图标库;禁止硬编码颜色/字号/间距。
7. 密钥只走 `.env`(当前仅可选 `CTEXT_API_KEY`);禁止写入代码、文档、构建产物与日志。
8. 核心流程不得用 mock 数据、跳过校验或手改产物冒充 `ht build` 结果。
9. Bug 在根因处修复:从数据/代码的第一性原理定位成因,禁止只在症状处打补丁。

## 会话协议

1. **开始**:读 `docs/gov/STATE.md` 和 `.devinit/manifest`;涉及技术选型、组件、集成或设计时,先查已关联 Dev-Kit(`/Users/yuantk/Developer/dev-kit`)的 `catalog/assets.json` 及相关资产说明,按任务优先评估并记录采用/不适用原因;来源不可用时报告。
2. **规划**:架构/跨模块改动先读 `docs/gov/01-ARCHITECTURE.md`;写代码前读 `docs/gov/02-CONVENTIONS.md` 对应小节;数据任务先读 `docs/verification-protocol.md`。对本任务涉及的规则做有效性检查:核对适用范围、依据及与用户目标、现有代码和新证据是否冲突;发现疑似错误时登记 `governance` 线程,按 devinit 的 sync/update 流程处理。
3. **领取任务**:在 STATE.md「在途任务」登记任务 ID、owner、基线、允许范围和更新时间;超过阈值只标记需确认。
4. **完成(Definition of Done)**:记录验证证据 → 更新 STATE.md(任务状态+变更摘要)→ 涉及接口/模块时更新 03-MODULES.md → 涉及数据规则时确认 verification-protocol 一致性;评估可复用素材登记 reuse;是否 git commit 按授权执行。
5. **发现即记录**:新发现的 bug/技术债/待评估项立即写入 STATE.md「Open Threads」,不顺手修。
6. **并行开发**:trunk-based 短分支;不改动他人未归属文件与既有任务基线。
7. **规则变更**:修改 02-CONVENTIONS / 01-ARCHITECTURE / 05-DESIGN / 本文件硬规则时,必须同步 append 一条 ADR 到 04-DECISIONS.md 并标明取代的旧决策。
8. **持续回流授权**:用户已授权在实际项目任务中维护默认 Dev-Kit(`/Users/yuantk/Developer/dev-kit`)源码;满足证据、去敏、验证及宿主权限要求时按 devkit-protocol 执行回流,未满足则登记候选;不自动修改其他项目、不自行安装技能、不因此提交/推送/部署。

## 常用命令

| 用途 | 命令 |
|------|------|
| 数据校验(R0+R1) | `cd pipelines && uv run ht verify` |
| 数据构建(→web/public/data) | `cd pipelines && uv run ht build` |
| 质量报告 / 纪年换算 | `uv run ht report` / `uv run ht era 贞观 14` |
| Python 测试 / Lint | `uv run pytest` / `uv run ruff check .`(均在 pipelines/) |
| 前端类型检查 / 测试 / 构建 | `pnpm typecheck` / `pnpm test` / `pnpm build`(均在 web/) |
| 本地预览 | `pnpm -C web dev`(开发)或 `pnpm -C web preview`(产物) |

## 文档地图

| 文件 | 何时读 |
|------|--------|
| `docs/gov/STATE.md` | 每次会话开始 |
| `docs/gov/00-OVERVIEW.md` | 需要项目背景/术语时 |
| `docs/gov/01-ARCHITECTURE.md` | 改架构、跨模块、新增模块前 |
| `docs/gov/02-CONVENTIONS.md` | 写代码前(按节读) |
| `docs/gov/03-MODULES.md` | 改模块前(边界+禁区) |
| `docs/gov/04-DECISIONS.md` | 想偏离现行规则前 |
| `docs/gov/05-DESIGN.md` | 改设计令牌、组件或页面风格前 |
| `docs/verification-protocol.md` | 任何数据录入/校验/建模任务前 |
| `docs/project-plan.md` + `docs/research/` | 需要路线图、数据源与许可依据时 |
