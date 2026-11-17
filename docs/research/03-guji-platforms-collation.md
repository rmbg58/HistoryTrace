# 调研报告三:古籍平台、OCR 工具与校勘方法论

> 调研日期:2026-11-18。"实测"者为直接调 API/curl 验证;未核实处已标注。ctext 主站反爬(403),其 API 经 Wayback 存档与第三方索引核实。
> 本报告 §五的机制建议已扩展为正式设计:[../verification-protocol.md](../verification-protocol.md)。

## 一、古籍全文在线平台

### 1.1 ctext.org(中国哲学书电子化计划,CTP)

- **覆盖**:超 30,000 部文献、50 亿字+,自称最大先秦两汉古籍在线图书馆。文本分两体系:**原典体系**(稳定校过的核心文本,URN 如 `ctp:analects`、`ctp:han-shu`)与**维基体系**(用户贡献,`ctp:wb{id}`)。实测:《汉书》《后汉书》在原典板块;《元史》等后世正史在维基板块——**正史类质量不一,先秦两汉是强项**。原典带版本信息(实测《论语》底本"武英殿十三經注疏")。
- **API(实测)**:域名 `https://api.ctext.org/`。`getstatus`/`gettextinfo`(书目元数据、版本、朝代)/`searchtexts` 匿名可用;`gettext` 需鉴权("請使用已註冊的IP地址,或提供有效的apikey")。官方定位是"将内容引入在线工具"而非批量下载;错误码含 ERR_REQUEST_LIMIT,**具体限流数值未公开**。另有 OpenSearch 风格插件 API 与实体 LOD(RDF/TTL)。
- **版权**:使用条款"**嚴禁使用自動下載軟体下載大量網頁,違者自動封鎖**";引用须附 ctext.org 链接。古籍原文公版,但站点整理层(标点、英译、校订)有版权。
- **适用**:逐条精查与 URN 对齐(**引用核验式低频调用**),保留 URN 作溯源键;**不作批量语料源**。

### 1.2 识典古籍(shidianguji.com)

- 北大—字节跳动数字人文开放实验室,2022-10 上线。390 部(《四部丛刊》约 3000 万字)→ 2024-07 约 6,820 部 → 近期报道 4.7 万部+(数字随时间增长,引用需写核查日期)。含《四库全书》《百衲本二十四史》类来源(浙大导航页所述,未逐项核实)。
- **哈佛燕京关系**:2023 年哈佛燕京将全部善本影像(约 13,300 部/15 万册)无偿捐赠北大,宋刻《十诵律》、元刻《隋书》、明抄《永乐大典》等在识典上线;注意与山东大学"全球汉籍合璧工程"是不同项目。
- **整理平台(与校验机制最相关)**:流程 = **OCR → 文字校对 → 对勘 → 标题识别校对 → 分段 → 标点 → 实体校对 → 元数据修改 → 任务分发**;质量分**粗校(机器)/精校(人工)**两级;报道 OCR 准确率超 96%、自动标点 94%、NER 约 98%;3.4 万志愿者修订超 13 亿字。**这是"AI + 众包 + 专家"三级流水线的现成范本。**
- **API/批量下载**:未发现官方开放渠道(未核实其是否存在)。**适用**:人工核验的阅读界面(图文对照、底本影印)与方法论样板,不可批量抓取。

### 1.3 维基文库(zh.wikisource.org)——批量基准语料首选

- **覆盖(实测)**:`Category:二十四史` 存在,成员含三国志、元史、北史、北齐书、南史、南齐书、史记、周书、宋史、宋书、后汉书等,2026-11 仍更新。
- **获取(实测)**:标准 MediaWiki API 匿名可用——`action=query&generator=categorymembers&gcmtitle=Category:二十四史&prop=revisions&rvprop=content` 批量取 wikitext;另有 `action=raw`、Special:导出(XML dump)、dumps.wikimedia.org 全站转储。需遵守 Wikimedia API 礼仪(UA 标识、串行、限速)。
- **License(实测 siteinfo)**:站点级 **CC BY-SA 4.0**;古籍原文公版,录入贡献按 CC BY-SA,批量再分发应署名。部分页面配影印件(PD)。
- **质量**:多据民国以前刻本/早期排印本录入,ProofreadPage 页面级状态标记,质量不均;与中华书局点校本无涉(规避点校本版权)。**适合作为"对校"中的一方而非权威方。**

### 1.4 其他:汉典、国学大师、殆知阁、古诗文网

- **殆知阁**:原站约 2020 关停;GitHub 镜像 [garychowcmu/daizhigev20](https://github.com/garychowcmu/daizhigev20)(约 5GB、16,000 余种、约 20 亿字 TXT)。原文公版但来源网络流传、**错讹较多、无版本信息——只能当低权重旁证(D 级)**。
- **国学大师**:约 2021 永久关停。**关键判例:2012 年中华书局诉国学网胜诉**——法院认定**现代学者点校本(如中华书局二十四史点校本)享有著作权**。红线:**任何转录"中华书局点校本"体系文本的行为都有明确法律风险。**
- **汉典**(zdic.net):字典为主,无批量开放数据(未核实 API)。
- **古诗文网**:注释/译文/赏析属编辑性创作 + 反爬 + 商业运营,**爬取再分发风险高**,仅人工查阅。
- **总原则**:古籍**原文**(刻本/公版)无版权;**点校、标点、注释、译文**受著作权保护。校验中引用文本应回溯影印底本或公版来源;点校本只"参校"不"转录"。

### 1.5 权威影印底本来源(A 级"回到善本"层)

- **哈佛燕京善本**:Harvard CURIOSity(curiosity.lib.harvard.edu/chinese-rare-books),4,200 部/5.3 万卷全部数字化,免费浏览/下载。
- **中国国家图书馆**:中华再造善本、善本影像库(read.nlc.cn 读者门户)。
- **中华经典古籍库**(中华书局):点校本授权库,机构订阅,**不可爬取**,可作人工核验对照。

## 二、古籍 OCR 与数字化整理工具

- **PaddleOCR(PP-OCRv5)**:单一模型支持简体、**繁体**、手写、**竖版**、拼音、生僻字;较 v4 精度 +13pt,古籍场景检测 +43pt、生僻字 +95pt,微调后古籍字符准确率 94%+(官方与报道,细节数字未独立核实)。**自建古籍 OCR 管线应直接用 PP-OCRv5**;竖排需检测后按列重排。
- **GitHub 生态(实测在线)**:[bytedance/AncientDoc](https://github.com/bytedance/AncientDoc)(中文古籍文档 VLM 评测基准)、[daiuuuuu/guji-ocr](https://github.com/daiuuuuu/guji-ocr)(OCR→页序重排→纠错三 Agent 流水线)、esun-ai/traditional-chinese-text-recogn-dataset(2,150 万+合成繁体图像)、HF `ZihCiLin/traditional-chinese-ocr-synthetic`(410 万图文对)、NiuTrans/Classical-Modern(文言-白话平行)、Jihuai-wpy/bert-ancient-chinese。主题页 topics/ancient-text、topics/chinese-classics 可持续跟进。
- **EvaHan**:古籍/历史文档 OCR+NER 国际学术评测,可作横向参照。

## 三、校勘学方法论:"四校法"及其数字化映射

陈垣《校勘学释例》(1959 中华书局;原名《元典章校补释例》,1931)卷六"校法四例",原文经识典所藏影印本核实:

1. **对校法**:"以同书之祖本或别本对读,遇不同之处,则注于其旁"。**最简便、最稳当**。
2. **本校法**:"以本书前后互证,而抉摘其异同,则知其中之谬误"(目录对正文、前文对后文)。
3. **他校法**:"以他书校本书。凡其书有采自前人者,可以前人之书校之;有为后人所引用者,可以后人之书校之;其史料有为同时之书所并载者,可以同时之书校之"。范围广、用力劳,"非此不能证明其讹误"。
4. **理校法**:"遇无古本可据,或数本互异而无所适从之时,则须用此法。此法须通识为之……**故最高妙者此法,最危险者亦此法**"。

### 数字化映射

| 四校法 | 数字化对应 | 自动化程度 | 输出 |
|---|---|---|---|
| 对校 | 同书多来源全文比对(维基文库 vs ctext 原典/维基 vs 殆知阁镜像 vs 自有 OCR),CollateX/diff 按字对齐,异文落库 | **高** | 客观异文表 |
| 本校 | 单来源内部一致性:字频/N-gram 离群、人名字号官职前后一致、目录-正文对齐、纪年干支自洽 | **高** | 可疑点清单(不直接改字) |
| 他校 | 跨文献引文网络:类书/《资治通鉴》/方志/文集平行记载检索比对;正史互见 | **中**(检索自动,判等同半自动) | 平行文本聚类+异文 |
| 理校 | LLM/规则推理(避讳、字形讹变、音韵通假、地理常识),**只生成"校勘建议"** | **低,仅辅助** | 带理由的推断,标记"理校·待复核",永不自动定论 |

陈垣对理校的警告直接支持工程铁律:**理校类结果永远不能进入"已验证"状态,只能进人工复核队列,且须记录推理依据。**

### 自动比对工具现状(实测)

- **CollateX**(collatex.net):GPL,Java 1.7.1 + Python(PyPI 仍在发版),图对齐算法,数字 Scholarly Editing 事实标准;中文需自定义 tokenizer(按字切分天然适合)。
- **Juxta / Juxta Commons**:**已死**——域名已被重定向至垃圾站,**不要再引用**;源码在 GitHub(performant-software/juxta-service)可自托管但不建议新依赖。
- 备选:diff/difflib 级对齐(中文按字 token 后效果尚可)、TRACER(多语对齐,学术系统,未深入核实)。

## 四、数字人文的校验、对齐与溯源实践

### 4.1 OpenRefine / Wikidata reconciliation

- 打分 0–100,"auto-match with high confidence"阈值可调(社区通常 85–100 才自动);可用名称+年代+别号多列细化打分。
- 学术调查(arXiv 1906.08092):自动打分对最终决策的指导价值有限——**社区共识是"按分数分面 + 人工复核",自动只处理极高置信区间**。
- 可借鉴:**置信度与"自动采纳阈值"分离;中等分数一律进复核;judgment(人工确认/否决)作为一等数据保存**。

### 4.2 权威档 / 规范控制

- **Getty TGN**:地名叙词表,LOD(vocab.getty.edu,SPARQL),含历史地名/坐标/层级/书目出处;中国覆盖有限,与 CHGIS 互补。
- **VIAF**(OCLC):聚合 37 家规范档(含国图),跨语言人物消歧;**2025-01 改版**,接入前需确认现行接口。
- **CBDB**:约 65.8 万人,含人物-地址-职官,与法鼓文理学院人名/地名规范库做过对接清洗;API 支持按 ID/人名查询。**人物-地点-职官交叉校验的关键权威源。**

### 4.3 溯源(provenance)记录标准

- **W3C PROV-O**:Entity/Activity/Agent,`wasGeneratedBy`/`wasDerivedFrom`,可建模"某引文由某人于某时刻通过某校验轮次产出"。
- **著录规范**:GB/T 7714-2015(参考文献,古籍含版本项/卷次页码)、GB/T 3792.7《古籍著录规则》、文旅部《古籍元数据规范》。**建议引文键用结构化字段(书名/卷次/篇名/版本底本/叶码/数字 URN),展示层再渲染为 GB/T 7714 或传统格式。**
- 稳定溯源键:ctext URN(`ctp:han-shu/di-li-zhi`)、维基文库页面标题 + lastrevid(实测 API 返回)。

### 4.4 地理数据质量控制参照(最值得借鉴)

- **CHGIS V6**:许可"free for academic research, no commercial use, resale, or redistribution";设计上(逐年政区时间序列、县/府层级)是历史政区底图基准。
- **WHG(World Historical Gazetteer)** 的数据模型与质控设计:
  - **以 attestation(佐证)为核心**:Thing 本身不直接拥有名称/几何/时段,一切经由"attestation = 断言 + 来源 + certainty(0.0–1.0)+ 时段"给出;
  - 每条断言**必须**带文献引用/数据集 ID/贡献者——"cite your sources for every claim";
  - **冲突信息不合并**("don't merge conflicting information"),矛盾陈述共存,争议用 meta-attestation("关于断言的断言")记录学术分歧;
  - 不确定性显式建模于三层:**空间**(精度如 ±5km)、**时间**(earliest/latest + 精度描述符)、**断言**(certainty + 限定词)。

## 主要来源

[ctext API 存档](https://web.archive.org/web/2024/https://ctext.org/tools/api/zh) / [ctext FAQ](https://ctext.org/faq/zhs) / [北大数字人文:识典古籍](https://pkudh.org/project/shidianguji) / [识典古籍](https://www.shidianguji.com/zh) / [维基文库](https://zh.wikisource.org/wiki/Wikisource:%E9%A6%96%E9%A1%B5) / [MediaWiki API](https://www.mediawiki.org/wiki/API:Get_the_contents_of_a_page/zh) / [殆知阁镜像](https://github.com/garychowcmu/daizhigev20) / [中华书局诉国学网报道](http://collection.sina.com.cn/gjsb/20120910/170483974.shtml) / [点校本著作权分析](https://www.ciplawyer.net/articles/118835.html) / [PaddleOCR](https://github.com/PADDLEPADDLE/PADDLEOCR) / [PP-OCRv5](https://aistudio.baidu.com/modelsdetail/28601) / [哈佛 CURIOSity 中文善本](https://curiosity.lib.harvard.edu/chinese-rare-books) / [校勘学释例(识典影印本)](https://www.shidianguji.com/book/CADAL02119837/chapter/1lm8p72filp1v) / [CollateX](https://collatex.net) / [OpenRefine Reconciling](https://openrefine.org/docs/manual/reconciling) / [reconciliation 学术调查](https://arxiv.org/html/1906.08092v2) / [Getty TGN](https://vocab.getty.edu) / [VIAF](https://www.oclc.org/developer/api/oclc-apis/viaf.en.html) / [W3C PROV-O](https://www.w3.org/TR/prov-o) / [GB/T 7714-2015](https://journal.ustc.edu.cn/uploadfile/yjsjy/20161108/GB%20T%207714-2015%E4%BF%A1%E6%81%AF%E4%B8%8E%E6%96%87%E7%8C%AE-%E5%8F%82%E8%80%83%E6%96%87%E7%8C%AE%E8%91%97%E5%BD%95%E8%A7%84%E5%88%99.pdf) / [WHG concepts v4](https://github.com/WorldHistoricalGazetteer/documentation/blob/main/content/v4/user-guide/getting-started/concepts.md) / [WHG API](https://whgazetteer.org/content/technical/apis.html)
