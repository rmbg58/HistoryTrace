# 调研报告一:历史地图开源项目与 GIS 数据源

> 调研日期:2026-11-18。所有条目基于实际抓取的 GitHub API / Harvard Dataverse API / WebSearch 结果,star 数为当日值。未核实处已标注。

## 一、交互式中国历史地图项目(GitHub)

### 1.1 DeanChensj/jiangshan-map(江山时序)——与本项目需求匹配度最高

| 项目 | 内容 |
|---|---|
| 地址 | https://github.com/DeanChensj/jiangshan-map |
| Star / Fork | 7,606 / 909("中国历史地图"关键词星数第一) |
| License | **GPL-3.0**(代码);府级边界图层源自 CHGIS V6 + Hartwell GIS,**学术非商用、不含在 GPL 中、默认不可再分发** |
| 最近更新 | 2026-11-17(活跃) |
| 技术栈 | 原生 HTML/CSS/JS(无框架),Docker(nginx)部署,含 Node MCP server、Python 地形瓦片工具 |
| 数据覆盖 | 403 BCE – Present,18 个朝代,198 个疆域快照;人物行迹(李白/苏轼/玄奘)、事件线(安史之乱)、古地名测验 |
| 数据格式 | 自研拓扑去重 VLQ 压缩包;`scripts/export_geojson.js` 可导出标准 GeoJSON(EPSG:4326),403 BCE–1948 |
| 关键功能 | **Trace Place:点选任一古城/关隘,展示其跨越 18 个时代的名称与政区演变卡片**——与"点选地点查看历代名称"需求完全对应 |
| 线上演示 | https://deanchen.me/jiangshan-map/ |

数据来源声明(README 核实):政权边界起始于 aourednik/historical-basemaps 后手工重绘;府/郡/州界来自 CHGIS V6 与 Hartwell GIS(学术非商用);现代省界来自阿里 DataV GeoAtlas;明确声明**不包含**谭其骧《中国历史地图集》图幅(仅作学术校核参考)。

**可复用性:高(非商用)/ 中(商用)**。年份→快照 index.json→bbox 过滤点面判断、时间轴 scrub、相邻快照"幽灵边界"diff 等实现范式可直接参考;但 GPL-3.0 传染 + CHGIS 图层限制,闭源商用不可直接拿数据。

### 1.2 其他交互地图项目(均已核实)

| 仓库 | Star | License | 更新 | 说明 / 可复用性 |
|---|---|---|---|---|
| [hopechen067/MapStage](https://github.com/hopechen067/MapStage) | 531 | MIT | 2026-10 | MapLibre 叙事历史地图"舞台":羊皮纸风格、路线动画、seek(t) 截帧。MapLibre 路线直接模板。**中高** |
| [gonnavis/Timeline](https://github.com/gonnavis/Timeline) | 448 | 无 | 2026-05 | 时间段条 ↔ 历史地图联动(轻量 JS)。**中** |
| [guaner-334/civ-atlas](https://github.com/guaner-334/civ-atlas) | 574 | AGPL-3.0 | 2026-11 | 虚构星球历史推演(世界观创作),TS + 地图 + 编年史架构可借鉴。**中(仅技术)** |
| [cadicex/history_map](https://github.com/cadicex/history_map) | 232 | 无 | 2024-09 | 谭其骧《中国历史地图集》扫描版浏览软件(约 375MB)。**扫描图版权归地图出版社,再分发风险高。低** |
| [imbian/chinese_historical_map](https://github.com/imbian/chinese_historical_map) | 45 | 无 | 2024-03 | 谭图扫描版(约 425MB)。版权风险,**低** |
| [jin-apple467/china-historical-maps](https://github.com/jin-apple467/china-historical-maps) | 3 | 无 | 2026-05 | 谭图高清扫描浏览器(HTML)。**低** |
| [zinging/chinese-history-atlas](https://github.com/zinging/chinese-history-atlas) | 47 | MIT | 2026-11 | 77 帝时间线与疆域 + 22 位文人行迹。**中** |
| [lisongjianustc/shanheji](https://github.com/lisongjianustc/shanheji) 山河纪 | 2 | MIT | 2026-10 | TS,夏商周至明清疆域 + 事件时间轴,小而 license 干净。**中** |
| [wjt0321/china-history-river](https://github.com/wjt0321/china-history-river) | 1 | MIT | 2026-06 | 数字博物馆风格时间轴 + 疆域。**中** |
| [wang8271/china-history-3d](https://github.com/wang8271/china-history-3d) | 4 | 无 | 2026-07 | 2700 年疆域变迁 3D 地形。**低-中** |
| [qiaoshouqing/xianmap](https://github.com/qiaoshouqing/xianmap) | — | MIT | — | 唐长安 110 坊叠加现代西安的滑块案例(单城市尺度参考) |

### 1.3 "发现中国"(ageeye.cn)核实结论

- ageeye.cn(曾用名"观沧海")是志愿者运营的知识地图平台,**未发现开源仓库**(GitHub 搜索 + WebSearch 双重确认)。
- 同一团队在"地图书"(ditushu.com)运营"**中国历史地图在线协作矢量化计划**":https://www.ditushu.com/book/33 ,以谭图为参考、从秦朝起分批矢量化(2020 首版含秦朝点数据 567 条),数据表页可浏览/下载。**未逐条验证数据格式与授权条款**,商用前需联系团队确认。可复用性:**中(方向对,授权不明)**。

## 二、历朝疆域 GeoJSON / Shapefile 数据集

### 2.1 CHGIS V6(哈佛 CGA + 复旦史地所)——学术标准数据源,已逐层核实

- 官网 https://chgis.fas.harvard.edu ;数据页 https://chgis.fas.harvard.edu/data/chgis/v6 ;Dataverse:https://dataverse.harvard.edu/dataverse/chgis_v6
- **覆盖**:时间序列 221 BCE – 1911 CE(秦至清);全国快照层 1820 与 1911;另含 1990 人口普查层、明代驿路驿站层。V6 发布于 2016-12。
- **文件清单(Dataverse API 核实)**,全部为 shapefile zip:
  - 时间序列:`v6_time_pref_pgn_{utf,gbk}_{wgs84,xian80}.zip`(府级面)、`v6_time_pref_pts_*`(府级点)、`v6_time_cnty_pts_*`(县级点)
  - 1911 快照:`v6_1911_{prov,pref,cnty,twn}_{pgn,pts}_gbk.zip`
  - 1820 快照:`v6_1820_{prov,pref,cnty}_pgn/pts`、河流 `v6_1820_coded_rvr_lin`、湖泊 `v6_1820_lks_pgn`
  - 辅助:EULA PDF、README、数据字典、`Ming_Routes_2016.zip`、`Ming_Stations_2016.zip`
- **License**:独立 EULA——免费用于学术研究,**禁止商用、转售、再分发**。指定引用:"CHGIS, Version: 6. (c) Fairbank Center for Chinese Studies of Harvard University and the Center for Historical Geographical Studies at Fudan University, 2016."
- **下载**:Dataverse 直接下载,无需注册。
- **可复用性:高(学术/个人)/ 不可(再分发)**。唯一覆盖秦–清县以上政区+地名时间序列的权威数据,但许可封闭。

### 2.2 复旦禹贡 CHGIS V4 下载页

- https://yugong.fudan.edu.cn/CHGIS/sjxz.htm :时间序列(秦–清)、1820 层、1911 层、DEM;**MapInfo Tab 格式**,无需注册;2013 年后基本停更。**低-中**。

### 2.3 aourednik/historical-basemaps——最易用的 GeoJSON 边界集

- https://github.com/aourednik/historical-basemaps ,890 stars,GPL-3.0,2026-11 活跃,约 170MB。
- `geojson/` 目录:`world_bc10000` 到 `world_2010` 约 70 个"一年代一文件"的世界政区边界(WGS84),属性含 NAME、SUBJECTO、PARTOF、**BORDERPRECISION(1–3 级精度)**;自动生成 index.json;另有 `places.geojson`(聚落点,含 inhabitedSince/until)。
- 覆盖中国:每个时间切片含中国政权多边形,但为**全球尺度粗略边界,非逐朝代精细政区**。
- jiangshan-map 的政权边界即源自它再手绘。**可复用性:高(GPL 项目)/ 中(需遵守传染)**。

### 2.4 中研院 CCTS(中华文明时空基础架构)

- 官网 https://ccts.sinica.edu.tw/framework.html ;WebGIS https://gis.rchss.sinica.edu.tw/ccts
- 开放方式:**OGC WMTS 瓦片服务** `https://gis.sinica.edu.tw/ccts/wmts`(中研院自有版权,可直接加载);官网注册后可下载矢量图层;depositar 有元数据(https://data.depositar.io/dataset/wmts-sinica-ccts)。
- 覆盖:逾二千年历史图层(以谭图体系为底)。**WMTS 是影像瓦片非矢量**,做点选查询需自建查询层;矢量逐项 license 未核实。**中(底图瓦片好,交互数据层受限)**。

## 三、古今地名对照 / Gazetteer

### 3.1 World Historical Gazetteer(WHG)——许可最干净

- https://whgazetteer.org ;文档 https://docs.whgazetteer.org
- 规模:**220 万+ 历史地名记录、70+ 数据集**,收录 CHGIS 衍生数据(如 chgis_cnty_1911)。
- 许可:**公共数据 CC-BY-4.0 可下载**(2021-08 V2 公告);提供 Entity API 与 Reconciliation API。
- 代码:GitHub 组织 WorldHistoricalGazetteer(主站 website 仓库 v3 beta,文档侧称 BSD-3-Clause);样本数据 kgeographer/whg-data。
- **可复用性:高**。CC-BY-4.0 可直接再分发(含商用,附署名);中国深度不及 CHGIS,适合做补充/链接层。其 attestation 数据模型是本项目校验机制的核心借鉴(见调研报告三 §4.4)。

### 3.2 GeoNames

- https://www.geonames.org ,CC-BY-4.0,`alternatenamesV2.zip` 含 zh 变体名。定位"the world as it is right now"——**以现代地名为准,历史覆盖稀疏**,只适合今名基准层与坐标规范化。**中**。

### 3.3 CBDB(顺带核实)

- [cbdb-project/cbdb_sqlite](https://github.com/cbdb-project/cbdb_sqlite)(246 stars,2026-11 更新);最新版约 **65 万人物**,SQLite/Access 双格式,HuggingFace 镜像。
- 许可:CC BY-NC-SA 类条款;**中国大陆商业使用权 2018 年独占授予元引科技**(https://cbdb.hsites.harvard.edu/exclusive-commercial-license)。**中(非商用高,商用受限)**。详见调研报告二。

## 四、时间维度交互(时间滑块/朝代切换)前端参考

1. **jiangshan-map**——"年份快照"范式最完整:index.json(朝代年份区间→快照)+ 时间轴 scrub + 幽灵边界 diff + 按需加载做点选判断。原生 JS 无框架。
2. **hopechen067/MapStage**(MIT)——MapLibre GL 历史叙事、古地图皮肤、路线动画、时间 seek。
3. **ucmerced-giscenter/cliopatria**(Apache-2.0,https://github.com/ucmerced-giscenter/cliopatria)——时间滑块地图 + Cliopatria 历史政体边界 3400 BCE–2024 CE(世界尺度含中国政权,许可干净,**商用路线的可商用边界来源**)。
4. **gonnavis/Timeline**(448 stars)——历史时段条 + 地图切换轻量实现。
5. **aourednik/historical-basemaps** 自带 D3 v5 与 Leaflet 示例——年代 GeoJSON 渲染最短路径。

## 五、最值得复用的"数据 + 技术"组合建议

**开源非商用(效果优先):**
- 交互范式:深度参考 jiangshan-map 的时间轴快照法与 Trace Place(注意 GPL,建议参考范式自行实现)
- 数据主轴:CHGIS V6 shapefile(Dataverse 免注册)做县级以上政区+地名沿革底表,自转 GeoJSON 按朝代切片;政权粗边界用 aourednik/historical-basemaps 补全球语境;现代底图用阿里 DataV GeoAtlas + GeoNames
- 前端:MapLibre GL JS(无 token)+ 年份→GeoJSON 快照层切换 + 时间滑块

**若闭源/商用:**
- 排除 CHGIS(EULA 禁商用再分发)与 GPL 数据;地名沿革改用 **WHG 公共数据(CC-BY-4.0)** + GeoNames;疆界:①自行矢量化(参考地图书协作计划,需谈授权)②CCTS WMTS 底图(需确认条款)③**Cliopatria(Apache-2.0)**;CBDB 商用需经元引科技授权。

**一句话结论**:非商用最快路径 = CHGIS 数据 + jiangshan-map 架构范式 + MapLibre;干净许可路径 = WHG(CC-BY)+ Cliopatria(Apache-2.0)+ 自建沿革表——自建部分正是本项目校验机制的价值所在。

## 主要来源

[jiangshan-map](https://github.com/DeanChensj/jiangshan-map) / [CHGIS 官网](https://chgis.fas.harvard.edu) / [CHGIS V6 Dataverse](https://dataverse.harvard.edu/dataverse/chgis_v6) / [复旦禹贡 V4](https://yugong.fudan.edu.cn/CHGIS/sjxz.htm) / [historical-basemaps](https://github.com/aourednik/historical-basemaps) / [CCTS](https://ccts.sinica.edu.tw/framework.html) / [WHG](https://whgazetteer.org/public_data) / [WHG 许可公告](https://blog.whgazetteer.org/2021/08/05/version-2) / [CBDB 商用授权](https://cbdb.hsites.harvard.edu/exclusive-commercial-license) / [地图书矢量化计划](https://www.ditushu.com/book/33) / [发现中国](https://www.ageeye.cn/) / [MapStage](https://github.com/hopechen067/MapStage) / [cliopatria](https://github.com/ucmerced-giscenter/cliopatria)
