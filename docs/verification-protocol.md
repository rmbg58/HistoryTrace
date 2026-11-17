# HistoryTrace 多来源多轮次校验机制(Verification Protocol)

版本:v0.1(2026-11-18)
状态:设计稿(P0 阶段评审后冻结 v1.0)
依据:[调研报告三](research/03-guji-platforms-collation.md) 及各数据源核实结果

---

## 0. 设计原则(三个锚点)

1. **陈垣"四校法"的工程映射**(《校勘学释例》):对校/本校可全自动,他校半自动,理校仅辅助且**永不自动定论**——"最高妙者此法,最危险者亦此法"。
2. **WHG attestation 模型**:每条数据都是"断言 + 来源 + certainty";**冲突不合并**,矛盾陈述共存;不确定性在空间/时间/断言三层显式建模。
3. **OpenRefine/Wikidata reconciliation 实践**:机器分数只用于筛选与**降级**;任何升级到"已验证"的操作**必须有人工 judgment 记录**。

由此推出四条铁律:

- **R1 每条声明必有来源**(cite your sources for every claim);
- **R2 冲突不合并**(don't merge conflicting information);
- **R3 机器只降级不升级**;
- **R4 理校永不入库为定论**,只进复核队列。

## 1. 数据模型:Source / Claim / Attestation / Verdict

一切可展示的数据(地名沿革、事件、行迹、系年)统一建模为 **Claim(声明)**。Claim 不直接"是事实",而是"被若干佐证支撑、被若干裁决审核的断言"。

```
Source(来源)── Attestation(佐证)──▶ Claim(声明)──▶ Verdict(裁决)
   书/库/版本        定位+引文+certainty     断言内容      人工判断记录
```

### 1.1 Source(来源)

```json
{
  "id": "src_hanshu_ws",
  "type": "text",                       // text | geodata | reference | derived
  "title": "汉书",
  "jurisdiction": "汉书/卷二十八上/地理志上",
  "edition": "维基文库录入本(民国前刻本体系)",
  "tier": "C",                          // 来源分级,见 §2
  "license": "CC-BY-SA-4.0(录入层);原文公有领域",
  "access": { "method": "mediawiki-api", "key": "汉书记录页标题", "revid": "latest" },
  "retrieved_at": "2026-11-18"
}
```

### 1.2 Claim(声明)——核心实体

```json
{
  "id": "clm_000173",
  "subject": { "type": "place", "id": "plc_xi_an" },      // 现代锚点(今西安)
  "predicate": "name_in_period",                            // 见 §1.2.1 谓词表
  "object": { "name": "长安", "role": "京都·京兆尹治所" },
  "period": { "earliest": -202, "latest": 8,
              "calendar": "proleptic-julian", "precision": "year" },
  "attestations": [
    { "source": "src_hanshu_ws", "locus": "地理志上·京兆尹",
      "quote": "京兆尹,故秦内史,高帝元年属塞国,二年更为渭南郡,九年罢,复为内史。……", "certainty": 0.85 },
    { "source": "src_hg_hanshu_ctext", "locus": "ctp:han-shu/di-li-zhi",
      "quote": "……", "certainty": 0.8 }
  ],
  "verdicts": [
    { "round": "R3", "by": "@reviewer-a", "date": "2027-01-05",
      "decision": "accept", "basis": "两源文本一致;《元和郡县图志》关内道同" }
  ],
  "confidence": "G3",                     // 见 §5
  "status": "verified-multi-source",      // draft | machine-checked | cross-checked | verified | disputed
  "disputes": [],                         // 异说,见 §7
  "provenance": { "created_by": "@z", "created_at": "2026-11-20",
                  "pipeline_runs": ["run_20261120_001"] }
}
```

**谓词表(v0.1,随阶段扩展):**

| 域 | 谓词 | 说明 |
|---|---|---|
| 地名 | `name_in_period` | 某时段该地名为 X |
| 地名 | `belongs_to` | 某时段隶属某政区 |
| 地名 | `located_at` | 历史地名 → 现代坐标(带精度) |
| 政区 | `boundary_snapshot` | 某年政区界(引用几何,带 BORDERPRECISION) |
| 事件 | `occurred_at` / `occurred_when` | 事件地点/时间 |
| 人物 | `person_at` | 人物某年在某地(带事件类型:任官/贬谪/游历…) |
| 作品 | `written_at` / `written_when` | 作品创作地/系年 |
| 对齐 | `same_as` | 与外部库(CHGIS/WHG/CBDB/Wikidata)实体对齐 |

### 1.3 Verdict(裁决)

人工判断是一等数据,与机器分数分开存:`{ round, by, date, decision(accept/reject/prefer-X/keep-disputed), basis(依据引文), scope }`。Git PR 与提交记录构成天然审计链(§6.3)。

## 2. 来源分级(先分层,再校验)

| 层级 | 来源示例 | 权重 | 获取方式 |
|---|---|---|---|
| **A 影印善本** | 哈佛 CURIOSity 善本影像、国图中华再造善本 | 最高(对校"祖本"替代) | 人工/半自动对图 |
| **B 校勘整理本** | 识典古籍"精校"、(机构订阅内)中华经典古籍库 | 高 | 人工界面核对,**不爬取不转录** |
| **C 结构化公版库** | 维基文库(MediaWiki API,CC-BY-SA)、ctext 原典板块(URN 点查) | 中高 | API 批量(维基文库)/低频点查(ctext,遵守限流) |
| **D 开放语料镜像** | 殆知阁 GitHub 镜像、ctext 维基板块 | 中低(仅旁证) | 直接下载/API 点查 |
| **E 机器生成** | 自有 PP-OCRv5 输出、LLM 理校建议 | 最低,仅待验证输入 | 本地管线 |

规则:来源入库时必须登记 tier 与 license;**中华书局点校本体系文本一律拒收为"转录源",只能登记为"参校记录"**(B 级、quote 为空、仅记异文结论)。

## 3. 校验层次 L1–L5(四校法映射 + 对齐)

| 层 | 名称 | 方法 | 自动化 | 产出 |
|---|---|---|---|---|
| **L1 对校** | 多源全文比对 | 同一引文取 ≥2 个 C/D 级独立来源 + 自有 OCR,按字 token 化后 CollateX/difflib 对齐 | 全自动 | **异文表**(位置/各本文字/来源)。两源一致→过;不一致→挂"异文待决" |
| **L2 本校** | 来源内部一致性 | 卷次连续性、纪年干支换算自洽、人名字号职官前后一致、目录-正文标题对齐、字频/N-gram 离群 | 全自动 | 可疑点清单(只标记不改字) |
| **L3 他校** | 跨文献互证 | 类书(《太平御览》)/《资治通鉴》/《元和郡县图志》/《太平寰宇记》/方志/正史互见的平行记载检索与相似度聚类 | 半自动(检索自动,判等同人工) | 平行文本簇 + 异文 |
| **L4 理校** | 推理校勘 | LLM + 规则:避讳、字形讹变、音韵通假、地理常识(某年某地尚非某州) | 仅辅助 | **"理校·建议"** + 推理理由,强制进复核队列,永不自动落库 |
| **L5 权威对齐** | 实体消歧对齐 | 人物→CBDB/VIAF/Wikidata;地名→CHGIS(本地)/WHG/TGN;书目→ctext URN/维基文库 revid。OpenRefine 式打分 | 半自动 | same_as 声明:≥阈值自动建并标记 auto,中低分进复核;机器分与人工 judgment 双字段保存 |

## 4. 轮次安排 R0–R4(时间维度的"多轮")

校验不是一次性状态,而是**可重放的流水线**;每轮运行产出 run 记录(PROV-O:Activity/Agent/时间/输入输出哈希)。

```
R0 入库前 ─→ R1 机器全量 ─→ R2 交叉校验 ─→ R3 人工复核 ─→ (发布) ─→ R4 回归(来源更新触发) ─↺
```

- **R0 入库前**:格式/许可检查——是否点校本体系文本→拒收转录;license 登记;schema 校验。
- **R1 机器校验**:L1 + L2 全量跑,给每条 claim 计算机器置信分(§5.2)。
- **R2 交叉校验**:L3 他校 + L5 对齐,按"被地图图层引用的优先"排序处理。
- **R3 人工复核**:专家/贡献者处理 L4 理校建议与 R2 未决异文;裁决(Verdict)入库。
- **R4 周期性回归**:来源更新(维基文库修订、识典精校完成、CBDB 发版、CHGIS/WHG 更新)自动重跑 L1 差异检测,**只复核变化条目**;每次发布前全量回归。

## 5. 置信度分级 G1–G4

| 等级 | 判据 | 地图/界面展示 |
|---|---|---|
| **G4 已验证** | ≥2 个 C 级以上独立来源一致 + 无未决异文;或 A/B 级底本直核 + 人工裁决 | 正常实线展示 |
| **G3 多源一致** | ≥2 独立来源一致但未对影印本 | 实线 + "多源未核本"角标 |
| **G2 单源/有异文** | 仅一个来源,或存在未决异文 | 虚线/浅色 + 角标可展开异文 |
| **G1 存疑** | 仅机器 OCR 或理校建议;或来源互相矛盾 | 默认不渲染在正式图层,进复核队列 |

内部同时保存 0–1 连续 certainty(兼容 WHG),G1–G4 是其分档展示。

**机器置信分** = f(来源 tier 权重, 对校一致度, OCR 字符置信, L5 对齐分)。
**升降级规则(R3 铁律的落地)**:自动流程只允许下调(G4→G3→G2…)与维持;**任何上调必须伴随 Verdict 记录**。

## 6. 工程实现

### 6.1 数据即代码(Data as Code)

- `data/claims/` 下每条 claim 一个 JSON(YAML)文件,git 版本化;
- 每次数据变更 = Pull Request;PR 模板强制填写:来源、locus、quote、许可自查;
- CI(GitHub Actions)在 PR 上自动跑 R1(机器校验),输出报告评论;**CI 只能加"未决"标记,不能移除**。

### 6.2 复核队列 = Issue + PR 状态机

```
open(待复核) → in-progress(认领) → PR(提交裁决) → merged(闭环) / kept-disputed(存异)
```

队列条目自动生成于:异文未决、理校建议、L5 中低分对齐、R4 来源 diff、OCR 低置信字。条目附:上下文(前后文 + 影印图像链接,如哈佛 CURIOSity/识典图文对照页)、各源异文并排、机器分析、历史裁决。

### 6.3 溯源记录

- Git 历史 = Activity/Agent 审计链;文件内 provenance 字段记录管线 run;
- 引用键结构化:`{书名, 卷次, 篇名, 版本/底本, 叶码, 数字键(ctext URN | wikisource 页面+revid)}`,展示层渲染为 GB/T 7714 或"书名+卷次+篇名+版本"传统格式;
- 数据卡片必须可展开"来源与校验"面板:全部佐证(含 quote)、certainty、裁决历史、管线 run。

## 7. 争议与异说(采纳 WHG 模式)

- 同一 subject+predicate 不同来源给出不同 object 时,**全部保留为独立 claim**,互标 `disputes`;
- 主线展示"当前采信值"(由 Verdict 指定),其余为"异说",可切换**按来源视图**;
- 地图视觉降级:G3 以下虚线/半透明;粗精度边界(BORDERPRECISION 弱)视觉弱化并标注"示意";
- 理校内容永远以"校勘建议"样式呈现,与正文视觉区分。

## 8. 各数据域专项规则

| 域 | 必经校验 | 特别规则 |
|---|---|---|
| 地名沿革 | L1(维基文库×ctext×殆知阁)、L3(正史地理志×《元和郡县图志》×《太平寰宇记》)、L5(CHGIS 本地参照/WHG 对齐) | 同名异地、异名同地必须走 L5+人工;"约"字时段精度降档 |
| 疆界几何 | 来源精度标注 | 只分发干净许可几何(WHG/Cliopatria/自绘);CHGIS 派生层仅本地开发用 |
| 历史事件 | L1+L3(多史互见) | 时间地点不一致时,时间优先采信编年体(《资治通鉴》),地点存异说 |
| 作品系年 | L3+L4 | **默认 G2 以下**:无编年笺注依据的作品系年不得高于 G2;系年依据(年谱/笺注)必须登记为 Source |
| 诗人行迹 | L5(CBDB/Wikidata 对齐)+ 人工 | CBDB 地址为"生涯事件级",映射为 `person_at` 时 precision 标 event;"虚写"地名不落点(见 poetry-map 流程) |

## 9. 合规红线清单

1. 中华书局(及各出版社)点校本:只参校,不转录,不入库为文本;
2. CHGIS / CBDB:仅本地开发与校验参照,不随仓库分发;引用按其指定格式;
3. ctext:逐条低频点查 + 附链接,禁批量抓取;保留 URN 为溯源键;
4. 识典古籍:人工阅读核对,不爬取;
5. 维基文库批量文本:CC BY-SA 署名 + revid;
6. 谭其骧《中国历史地图集》扫描件:不使用、不分发;
7. 自建 claims 数据:许可待定(CC BY-SA 或 CC BY-NC,见 project-plan §5 决策点)。

## 10. 度量与验收

- 每次发布输出**数据质量报告**:各 G 级条目数、异文未决数、复核队列积压、来源覆盖矩阵(claim × source tier);
- P0 验收:种子集(如 10 地点 × 5 朝代)全流程走通,R0–R3 每轮有产物;
- 长期目标:核心图层(府级地名沿革)G3 以上占比 ≥ 90%。
