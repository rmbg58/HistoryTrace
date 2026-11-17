# 调研报告二:诗词文本、人物行迹与纪年换算数据

> 调研日期:2026-11-18。基于实际抓取的 GitHub API / Wikidata SPARQL / 各项目 README 与数据文件采样,未核实处已标注。

## 一、古诗词文本数据集

### 1.1 chinese-poetry/chinese-poetry(核实:GitHub API + README + 数据采样)

- **地址**:https://github.com/chinese-poetry/chinese-poetry
- **规模**:54,445 stars / 10,978 forks,约 227 MB 纯 JSON。README:**5.5 万首唐诗、26 万首宋诗、2.1 万首宋词**,唐宋近 1.4 万诗人 + 1.5 千词人。实测 `authors.tang.json` 含 3,675 位唐作者。
- **License**:**MIT**(LICENSE + README 双确认)。
- **目录**:全唐诗/、宋词、论语、诗经、楚辞、四书五经、蒙学、元曲、五代诗词、御定全唐詩、曹操诗集、纳兰性德、rank(名句)、strains(词牌)等;全唐诗目录 320 个文件。
- **字段(实测)**:
  - 唐诗 `poet.tang.0.json`:`{ title, author, paragraphs[], id(uuid) }`——**无朝代字段(靠目录)、无任何地理/编年信息**
  - 宋词 `ci.song.0.json`:`{ author, rhythmic(词牌), paragraphs[] }`——连 id 都没有
  - 作者表 `authors.tang.json`:`{ name, desc(繁体小传,自由文本), id }`——可从中挖掘生卒、籍贯、宦游线索
- **可复用性:高**。文本底座首选;但繁简未统一、无系年无地理,**时空维度需完全外建**。

### 1.2 snowtraces/poetry-source(核实:README)

- https://github.com/snowtraces/poetry-source ,113 stars,**MIT**。
- 诗 476,333 + 词 53,369 + 曲 804,共 530,506 条,覆盖秦汉至明清,含两个版本《全唐诗》;提供免费只读 API(`https://poetry-api.snowtraces.com/v1`,无需 Key)。
- **可复用性:高**(chinese-poetry 的跨朝代补充 + 现成 API)。

## 二、诗人/历史人物传记与行迹结构化数据

### 2.1 CBDB 中国历代人物传记资料库

- 官网 https://chinesecbdb.hsites.harvard.edu(哈佛费正清中心 + 北大中古史中心 + 台湾中研院;官网 403 反爬,部分条款经检索核实);SQLite 版 https://github.com/cbdb-project/cbdb_sqlite (246★);数据托管 https://huggingface.co/datasets/cbdb/cbdb-sqlite (7.68 GB,含历史版本)。
- **下载(实测 latest.json)**:最新版 `cbdb_20261114.sqlite3`,直链 zip 带 SHA-256 校验;仓库附外键约束、18 个便利视图、反规范化 ADDRESSES 表、一键 Colab。
- **License**:**CBDB Data Licensing Terms = CC BY-NC-SA 4.0**(署名-非商业-相同方式共享);**中国大陆商业使用权 2018 年独占授予元引科技**。
- **规模**:约 **657,909 人**(2026-05);7–19 世纪为主,**宋代最强,唐代相对薄弱**。
- **关键表**:BIOG_MAIN(人物)、ALTNAME_DATA(别名)、ASSOC_DATA(社会关系)、**BIOG_ADDR_DATA(人物地址,每条带 c_firstyear/c_lastyear 公元起讫 + 年号纪年双轨)**、ADDR_CODES/ADDR_BELONGS_DATA(地名与历代归属)、TIME_SEGMENTS、入仕官职表;`View_BiogAddrData` 视图含 reign info 和坐标。
- **评估**:**唯一具备"人物 × 地点 × 年份"三元组的规模化开源数据**;但地址是"生涯事件级"(某年任某地官),非逐年行迹。**可复用性:高(非商业)**。

### 2.2 Wikidata(实测:EntityData API + SPARQL)

- **License**:**CC0**(可商用,无署名义务)。
- 实测覆盖:李白 Q7071 共 183 属性(P569/P570 生卒、P19/P20 生卒地、P119 埋葬地、P937 工作地仅 1 处=长安);杜甫无 P937。SPARQL 统计:全库诗人 134,857 人,唐朝诗人 2,908 人,其中**有 P937 工作地的仅 2 人**——行迹级属性覆盖极低。
- **评估**:适合"诗人档案卡"(生卒、生卒地、画像、别号),**不适合行迹重建**;CC0 许可最佳,与 CBDB 交叉互补。**中-高**。

### 2.3 GitHub 上的"诗人足迹/唐诗地图"项目

| 项目 | Stars | 核实情况 | 评估 |
|---|---|---|---|
| [dingdjfjs-star/poetry-map](https://github.com/dingdjfjs-star/poetry-map) | 0(2026-11 仍更新) | README + 数据实测,见 §五 | 与目标功能**同构度最高**的参考实现 |
| [BinNong/meet-libai](https://github.com/BinNong/meet-libai) | 1,893 | README:李白知识图谱(Neo4j)+RAG,GPL-3.0 | 应用型,GPL 传染 |
| yuyuzou/shixingshanhe《诗行山河》 | 5 | 18 处名胜 × 诗词交互地图 | 演示级 |
| GrittingLeo/changzheng-poetry-map | 2, MIT | 毛泽东诗词长征行迹 | 单人专题,路线数据结构可参考 |
| shirenzuji.github.io 等 | 0 | 2022 停更,README 404 | 弃用 |

**结论:"诗人足迹"方向没有高星成熟开源项目,最高相关项目 0 star。**

## 三、诗人年谱/编年数据的开源情况

- GitHub 搜"年谱/编年/chronology"无专门数据集。现有最接近:
  1. **poetry-map 的 `data/routes.js`**:53 位诗人生平游历路线,每站 `{地名/坐标, year(含"约"标注), label(事件)}`——唯一可直接读取的结构化"诗人生平行迹"开源数据,规模小、人工简绘。
  2. meet-libai 的李白生平知识图谱(GPL)。
  3. CBDB 的 BIOG_ADDR_DATA(带年份地址事件)="机器可读的粗粒度年谱"。
- **王兆鹏团队"唐宋文学编年地图"**(https://sou-yun.cn/PoemGeo.aspx ,四川大学数字融合实验室):151 位唐宋诗人编年系地,最权威先例——**仅在线浏览,无下载、无 API、不开源**。只能对标其信息架构。
- **结论:单个诗人的精细年谱在开源世界是空白**,需从公有领域古籍(历代年谱刻本、已过版权期的今人整理本)自行整理。**这是功能链条中最大的数据缺口。**

## 四、中国历史纪年换算(年号/干支 ⇄ 公元)

| 库 | 核实 | License | 评估 |
|---|---|---|---|
| [rosemori/ChineseEraConverter](https://github.com/rosemori/ChineseEraConverter) | README:支持先秦君主在位纪年(周宣王三年→前825)、历代年号、传统月日/闰月/朔望晦/干支日、民国纪年、并立政权反查;格里/儒略双显 | **无 LICENSE(风险)** | 功能最全,先补 license 再用 |
| [Siyuan-chat/ming-zhengshuo](https://github.com/Siyuan-chat/ming-zhengshuo) | README:东亚年号双向互换(贞观十九年→645→日本大化元年),年份级,输出并行候选政权,面向 AI Agent | MIT | 年号换算主力 |
| [Hellohistory/HistoryChronology](https://github.com/Hellohistory/HistoryChronology) | README:前841–1911 完整年表(公元/干支/朝代/政权/帝王/年号),Qt 桌面软件内嵌 | Apache-2.0 | 年表数据完整,需抽取 |
| 6tail/lunar-javascript(1,757★)/lunar-python(702★)/lunar-go(349★) 等 | 检索核实:公历⇄农历⇄干支⇄儒略日、生肖节气,2026-11 活跃 | MIT | 干支/历法标准库,**不含年号表** |
| CBDB 内嵌 NIANHAO 表 | 实测存在(chn/pin/起讫年) | 随 CBDB(NC) | 权威年号对照,可导出交叉验证 |

**结论**:干支/历法用 6tail(MIT);年号⇄公元用 ming-zhengshuo(MIT)+ CBDB 年号表交叉验证;先秦王年与月日级换算等 ChineseEraConverter 补 license。

## 五、"作品-地点"关联数据与文学地理学项目

### 5.1 dingdjfjs-star/poetry-map(核实:README + 数据文件实测)

- https://github.com/dingdjfjs-star/poetry-map (在线版 https://dingdjfjs-star.github.io/poetry-map/)
- 规模:137 首经典诗词(55 位诗人)× 187 个古地名落点;53 条诗人游历路线(李白 14 站、苏轼 11 站、杜甫 9 站…);地名库约 192 条;人工考辨 53 项修正、17 处存疑。
- **License:无 LICENSE(未声明)**——建议仅作方法论参考或联系作者,重新整理而非复制。
- **数据结构(值得借鉴的 schema)**:
  - `gazetteer.js`:`{ id, name(古名), alias[](诗中异写), lat/lng(WGS84 今址), modern(今行政区划), type, note, debated, defaultFor(歧义裁决) }`
  - `routes.js`:`{ id, name, dynasty, stops: [{地名库id 或 lat/lng, year("约"标注), label(事件)] }`
  - `poems.source.js`(全诗+系年+注释)→ `tools/build.js` 自动地名识别/消歧/打点 → 核查报告
- **亮点流程**:"虚写排除"(如辛弃疾"西北望长安"不落点)的考据规则;歧义地名裁决字段。

### 5.2 搜韵"唐宋文学编年地图"

见 §三。**可复用性:低(仅对标产品)**。

## 六、数据组合建议(按许可分层)

1. **文本层(可商用)**:chinese-poetry(MIT)为底座 + poetry-source(MIT)补明清;两库均无系年,需自建。
2. **人物档案层(可商用)**:Wikidata(CC0)SPARQL 批量拉 2,908 位唐代诗人档案;CBDB(CC BY-NC-SA,**仅非商用**)做带年份地址/入仕事件,商用版仅作人工核对参照。
3. **行迹/编年层(最大缺口,需自建)**:种子用 poetry-map 53 条路线做 schema 原型(重新整理);主力方案 =「CBDB 生涯事件 + 公有领域年谱古籍(OCR/LLM 抽取"年份-地点-事件"三元组)+ 人工校对」,对标王兆鹏平台(151 人)但不搬数据。
4. **纪年层(可商用)**:6tail/lunar-*(MIT)干支 + ming-zhengshuo(MIT)年号 + CBDB 年号表交叉验证。
5. **地名坐标层**:非商用走 CHGIS;商用自采并借鉴 poetry-map 的 gazetteer 结构(alias + 歧义裁决 + 虚写排除)。

## 核心风险提示

- **时空信息的最大缺口在"作品级系年"**——任何开源库都不提供,必须自建并直面学术争议;
- CBDB 与 CHGIS 均 NC/禁再分发,**任何商业形态下直接打包这两个数据源不可行**;
- "诗人足迹"开源生态极不成熟(最高相关 0 star)——**竞品壁垒恰在数据而不在代码**,这正是本项目校验机制+自建数据的价值。

## 主要来源

[chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) / [cbdb_sqlite](https://github.com/cbdb-project/cbdb_sqlite) / [CBDB SQLite@HF](https://huggingface.co/datasets/cbdb/cbdb-sqlite) / [CBDB 官网](https://chinesecbdb.hsites.harvard.edu) / [Wikidata](https://www.wikidata.org) / [poetry-map](https://github.com/dingdjfjs-star/poetry-map) / [poetry-source](https://github.com/snowtraces/poetry-source) / [ming-zhengshuo](https://github.com/Siyuan-chat/ming-zhengshuo) / [ChineseEraConverter](https://github.com/rosemori/ChineseEraConverter) / [HistoryChronology](https://github.com/Hellohistory/HistoryChronology) / [6tail/lunar-javascript](https://github.com/6tail/lunar-javascript) / [搜韵诗词地理](https://sou-yun.cn/PoemGeo.aspx) / [川大数字融合实验室](https://dclab.scu.edu.cn/info/1020/1002.htm) / [meet-libai](https://github.com/BinNong/meet-libai)
