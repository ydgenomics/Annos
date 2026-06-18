https://gemini.google.com/app/cdc6e2f1c81c2fdf?is_sa=1&is_sa=1&android-min-version=301356232&ios-min-version=322.0&campaign_id=bkws&utm_source=sem&utm_medium=paid-media&utm_campaign=bkws&pt=9008&mt=8&ct=p-growth-sem-bkws&gclsrc=aw.ds&gad_source=1&gad_campaignid=20108148196&gbraid=0AAAAApk5BhnNtUcWb8NSu7R3LkjJkRncB&gclid=Cj0KCQjwv-LOBhCdARIsAM5hdKf6YFDNXBZvNyLYxGYuNL8-0Z9FFu78b5cJmmRTOt9lliFZgrHJwx8aAtxjEALw_wcB

在这篇研究中，**细胞类型基石基因（Cell-type foundational genes）** 的确定主要基于跨维管植物物种（包括石松类、蕨类、裸子植物和被子植物等6个代表性物种）的单细胞转录组数据整合与演化保守性筛选。其具体确定流程与核心标准如下：

### 1. 基石基因的概念定义

在算法和筛选启动前，研究对基石基因赋予了明确的生物学定义：它们必须是**超保守的核心基因（ultra-conserved core genes）**，在特定的细胞类型中高表达，对其功能的维持至关重要，并能作为该细胞类型身份和功能的核心标志物 。

### 2. 核心确定流程与筛选标准

* **跨物种同源关系的建立（双边比对）**：
为了避免将拟南芥作为唯一参考物种所带来的系统发育偏见（Bias），研究团队使用 **SAMap** 软件，以两两配对（Pairwise）的方式在所有6个维管植物物种之间建立了同源基因对（Homologous gene pairs）。


* **细胞簇整合与泛细胞群体（Pan-cell populations）划分**：
通过跨物种整合（利用 SAMap 和 SATURN 工具），将不同物种的单细胞图谱合并，划分出表皮（Epidermis）、木质部（Xylem）、韧皮部（Phloem）等宏观维管植物泛细胞群体（Pan-cell populations）。


* **保守性的定量筛选标准（最核心标准）**：
在划分好的各个泛细胞群体中，研究人员统计了同源基因在各物种间的保守分布情况 。**最终将“在至少4个物种中都保守存在且维持相应表达模式的同源基因”正式定义为该细胞类型的基石基因** 。


* **利用 Upset 图进行交集确定**：
通过 Upset Plot 分析各泛细胞群体中跨物种保守同源基因的交集分布，精准圈定出满足上述“$\ge 4$ 个物种保守”条件的基因集合 。例如，依此标准分别确定了 289 个表皮基石基因、234 个木质部基石基因以及 274 个韧皮部基石基因 。



### 3. 后续的功能与调控验证（辅助确认）

确定该基因集后，研究还通过以下多组学手段进一步验证了它们作为“基石”的可靠性：

1. 
**富集分析（GO Analysis）**：验证这些基石基因是否显著富集在与其对应细胞类型核心生理功能高度相关的通路上（如表皮基石基因富集在脂肪酸和角质层合成，韧皮部富集在蛋白质降解复合物等）。


2. 
**染色质可及性验证（scATAC-seq）**：在拟南芥中的分析表明，这些筛选出的基石基因在其对应的细胞类型中往往具有**显著更高的染色质可及性（Chromatin accessibility）**，证实了其活跃的顺式调控状态和关键调控地位 。


为了让复杂的跨物种细胞类型注释流程更加清晰直观，我将 **XSpeciesSpanner** 算法的流程总结为以下四个核心步骤：

---

### 🧬 XSpeciesSpanner 算法流程总结

1. **构建评分基因集 (Scoring Gene Set Construction)**
* **输入**：保守基因集 (Conserved gene set)。
* **处理**：将该基因集与 **SATURN 识别的基因**进行取交集（Overlap）过滤。
* **目的**：筛选出兼具保守性与高度生物学相关性的核心基因。


2. **同源蛋白质预测 (Homologous Protein Prediction)**
* **输入**：待查询物种的蛋白质（Query proteins）。
* **处理**：利用 **BLASTP** 序列比对工具，评估待查询蛋白质与上述构建基因集内蛋白质的相似性。
* **目的**：确立跨物种间的同源关系，为后续分析搭建桥梁。


3. **运行评分算法 (Scoring Algorithm)**
* **输入**：每个细胞簇（Cell cluster）的差异表达基因（DEGs）。
* **处理**：使用超几何分布（Hypergeometric distribution）检验，评估这些差异表达基因在保守基因集中的富集程度。
* **输出**：计算出 $p$-value，以此量化基因集与细胞簇之间关联的显著性。


4. **定义细胞类型 (Cell Type Definition)**
* **输入**：上一步得到的统计学显著性结果（$p$-value）。
* **处理**：应用一套顺序决策规则（Sequential decision rules）进行多级判断：
* 评估细胞簇关联的显著性。
* 判断其属于特定亚群（Subgroups）还是代表混合细胞类型（Mixed cell types）。
* 对无法明确归类的细胞簇标注为“未知（Unknown）”。


* **输出**：最终确定每个细胞簇的细胞类型标签。



---

**核心逻辑简述**：该算法首先**筛选核心保守基因**，随后通过 **BLASTP 建立跨物种同源性**，接着利用**超几何分布进行统计学富集评分**，最后通过多级决策树（顺序规则）完成细胞类型的精准注释与归类。