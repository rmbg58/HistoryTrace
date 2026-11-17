# 工程规范

> 写代码前按节读。规则变更须 append ADR 到 04-DECISIONS.md。
> 未经项目验证的技术偏好标为"试行"或"待确认",同条记录依据和复核条件;出现反例时按 devinit 的规则有效性检查修订,不把默认值当作永久约束。

## 语法与命名

- 语言版本:TypeScript(node 22,strict);Python ≥3.12(uv 管理,`pyproject.toml` + `uv.lock`)
- 命名:文件 kebab-case;类型/类 PascalCase;变量/函数 camelCase(TS)/snake_case(Py);常量 CONST_CASE;claim/source JSON 文件 `clm_*.json` / `src_*.json`
- TypeScript:`strict: true`;禁 `any`(未知结构用 `unknown` + 收窄);优先 type alias
- Python:ruff(format + lint);类型注解齐全;`ht` CLI 入口用 click/typer(择一后定,记 ADR)

## CSS / 样式与 UI 文案(UI 项目)

- 体系:原生 CSS + `@layer`(reset / tokens / base / components / utilities),无 CSS 框架、无组件库
- Token 来源:`web/src/styles/tokens.css`;**新增任何颜色/字号/间距/字体必须先加 token**,设计事实源:`05-DESIGN.md`(古风体系)
- 主组件体系:自绘 Web Components/TS 模块;禁止引入任何 UI 组件库(与古风自绘路线冲突)
- 组件分层:基础零件 → 组合组件(时间轴/沿革卡片/溯源抽屉)→ 页面区块(地图舞台/朝代带)→ 页面
- 图标:自绘 SVG(印章、关隘、都城等均为项目专属图形语言);不用第三方图标库
- UI 文案:简体中文;古籍引文保留原字(繁体/异体不转换);朝代年份用 tabular 数字;不加冗余说明性 microcopy
- 禁止:硬编码颜色/字号/间距;行内样式(动态地图样式参数除外,须集中一处)

## 数据与许可(项目特有硬约束)

- 发布产物(web 构建输出与 ht build 产物)只允许包含白名单来源数据,白名单唯一事实源:`data/registry/`(WHG CC-BY / Cliopatria Apache-2.0 / 维基文库 CC-BY-SA / chinese-poetry MIT / GeoNames CC-BY / 自建)
- CHGIS、CBDB 等受限数据只存在于 `data/_downloaded/`(gitignore),仅作本地校验参照,引用记录进 claim 的 verdict 而非 attestation 文本
- 中华书局点校本体系:不转录、不入库,只可登记"参校"结论(B 级、无 quote)
- 校验协议四铁律(R1 每条声明必有来源 / R2 冲突不合并 / R3 机器只降级不升级 / R4 理校永不自动定论)是数据层不可绕过的约束,实现于 `pipelines/ht verify`

## 依赖与个人底座

- 包管理器与锁文件:`pnpm-lock.yaml`(web)/ `uv.lock`(pipelines);新增依赖必须说明用途、许可兼容性与替代方案,并追加 ADR
- 个人模板:none;dev-kit 资产按任务评估记录采用/不采用原因(见 manifest.kit)
- 核心流程:不得用 mock 数据、跳过校验或硬编码产物冒充 `ht build` 结果

## 测试

- 框架:vitest(web)/ pytest(pipelines);命令:见 manifest.validation(当前 unverified,脚手架后回填)
- 策略:校验流水线(L1 对校、纪年换算、许可白名单、G 分级)必须有单元测试;`ht build` 产物有快照/金样测试;web 交互(时间轴切换、点选)关键路径冒烟
- 位置:与源文件同目录 `*.test.ts` / `tests/`

## 版本管理

- 分支模型:trunk-based,短分支验证通过即合 main
- Commit 规范:Conventional Commits(feat/fix/docs/chore/refactor/test);数据 claim 变更用 `data:` 前缀(试行)
- 版本号:0.x 直到 MVP(semver tag 从 v1.0 起)
- 发布流程:暂无(部署平台待定,OT-001);静态产物本地可复现构建

## 模块颗粒度

- 单文件软预算:300 行;超出先审查,不自动判定为错误
- 单模块软预算:10 个源文件;超出考虑拆子模块并更新 03-MODULES.md
- 函数/组件软预算:50 行;例外和依据记录到 STATE Open Threads
