gmt文件的格式
如何读取由eggnog-mapper注释的文件构建GO的gmt用于gseapy做富集


好的，我来完善这个 README，详细解释 GMT 文件格式以及如何从 eggnog-mapper 注释结果构建 GMT 文件用于 gseapy 富集分析。 

Read [](file:///d%3A/APP_cs/YD_learn/github/Annos/SCRIPTs/enrich/README.md)

现在我来写入完整的 README 内容。 

Queried session store

Created memory file [](file:///c%3A/Users/%E4%BA%BA/AppData/Roaming/Code/User/workspaceStorage/f58a3e5e68d44f441bed6c30ca0c2401/GitHub.copilot-chat/memory-tool/memories/repo/enrich-readme.md)

现在让我将内容写入 README.md 文件。 

Read [](file:///d%3A/APP_cs/YD_learn/github/Annos/SCRIPTs/enrich/README.md)

由于我没有文件编辑工具，我将为你展示完整的 README.md 内容，你可以直接复制替换到文件中：

---

```markdown
# 富集分析工具 — GMT 文件构建与 gseapy 使用

## GMT 文件格式

GMT (Gene Matrix Transposed) 文件是 GSEA (Gene Set Enrichment Analysis) 使用的标准基因集格式。

### 格式结构

每行代表一个基因集（如一个 GO term），由 **制表符 (Tab)** 分隔，结构如下：

```
<基因集名称>\t<描述信息>\t<基因1>\t<基因2>\t<基因3>\t...
```

| 列 | 内容 | 说明 |
|---|---|---|
| 第1列 | 基因集名称 | 如 `GO:0006915` 或 `apoptotic_process` |
| 第2列 | 描述信息 | 可选的描述文本，无描述时常用 `NA` 或留空 |
| 第3列起 | 基因列表 | 属于该基因集的基因符号/ID，每个基因一列 |

### 示例

```
GO:0006915	apoptotic_process	TP53	BAX	BCL2	CASP3	CASP9
GO:0007049	cell_cycle	CDK1	CCNB1	CDK2	CCNA2	CDK4
GO:0006955	immune_response	CD4	CD8A	IL2	IFNG	TNF
```

> **注意**：必须是 **Tab 分隔**，不是空格或逗号。这是新手最容易出错的地方。

---

## 从 eggnog-mapper 注释构建 GMT 文件

### eggnog-mapper 输出格式

eggnog-mapper 的注释结果通常是一个以 `#` 开头的制表符分隔文件，关键列包括：

| 列名 | 说明 |
|---|---|
| `query` | 基因/蛋白 ID |
| `GOs` | 以逗号分隔的 GO term（如 `GO:0006915,GO:0007049`） |
| `Description` | 功能描述 |
| `Preferred_name` | 基因名 |

### 构建 GMT 的 Python 脚本

以下脚本读取 eggnog-mapper 注释文件，提取 `query`（基因）和 `GOs`（GO term），构建 GMT 格式文件：

```python
import pandas as pd
from collections import defaultdict

# 1. 读取 eggnog-mapper 注释
# 跳过以 # 开头的注释行
eggnog_file = r"D:\APP_cs\Edge-download\jt.emapper.annotations"
df = pd.read_csv(eggnog_file, sep="\t", skiprows=4, skipfooter=3, engine="python")

# 只保留有 GO 注释的行
df = df[df["GOs"].notna() & (df["GOs"] != "-")]

# 2. 构建 GO term → 基因列表 的映射
go2genes = defaultdict(set)
for _, row in df.iterrows():
    gene_id = row["#query"]  # 或 row["Preferred_name"]
    go_terms = str(row["GOs"]).split(",")
    for go in go_terms:
        go = go.strip()
        if go and go != "-":
            go2genes[go].add(gene_id)

anno_file = r"D:\APP_cs\YD_learn\omics4plant\WORKFLOW\Enrich\DATA\go_obo_result.csv"
df2 = pd.read_csv(anno_file, sep=",")
go2name = dict(zip(df2["GO_ID"], df2["Name"]))  # 构建映射字典

# 3. 写入 GMT 文件（带注释）
with open("go_eggnog.gmt", "w") as f:
    for go_term, genes in go2genes.items():
        gene_list = "\t".join(sorted(genes))
        # 获取 GO term 的名称，若找不到则用 "NA"
        go_name = go2name.get(go_term, "NA")
        # 格式：GO_term\tGO_name\tgene1\tgene2\t...
        f.write(f"{go_term}\t{go_name}\t{gene_list}\n")

print(f"共构建 {len(go2genes)} 个 GO terms 的 GMT 文件")
```

### 使用 gseapy 进行富集分析

```python
import gseapy as gp

# 方式1：直接使用 GMT 文件
enrich_result = gp.enrichr(
    gene_list=["TP53", "BAX", "BCL2", "CASP3"],  # 你的目标基因列表
    gene_sets="go_eggnog.gmt",                     # 上面构建的 GMT 文件
    organism="human",
    outdir="enrichment_results"
)

# 方式2：直接从 DataFrame 构建基因集字典
go_dict = {go: list(genes) for go, genes in go2genes.items()}
enrich_result = gp.enrichr(
    gene_list=["TP53", "BAX", "BCL2"],
    gene_sets=go_dict,    # 直接传入字典
    organism="human",
    outdir="enrichment_results"
)

# 查看结果
print(enrich_result.results.head())
```

### 完整流程脚本

参考同目录下的 `enrichment.py` 脚本，整合了上述完整流程。

---

## 常见问题

### Q1: gseapy 报错 "No genes in your gene_set were found"

- 检查 GMT 文件中的基因 ID 是否与你的基因列表中的 ID 类型一致（如都是 Symbol 或都是 Ensembl ID）
- 检查 GMT 文件是否真的是 Tab 分隔

### Q2: eggnog-mapper 输出中 GOs 列为空或 `-`

- 确保 eggnog-mapper 运行时使用了 `--go_evidence non-electronic` 或类似参数
- 部分序列可能没有 GO 注释，这是正常的

### Q3: 如何验证 GMT 文件格式正确？

```bash
# 检查分隔符是否为 Tab
head -1 go_eggnog.gmt | cat -A
# 正确输出应显示 ^I 作为分隔符（Tab 的表示）
```

---

## 参考

- [gseapy 官方文档](https://gseapy.readthedocs.io/)
- [eggnog-mapper 官方文档](http://eggnog-mapper.embl.de/)
- [GSEA GMT 格式说明](https://software.broadinstitute.org/cancer/software/gsea/wiki/index.php/Data_formats#GMT:_Gene_Matrix_Transposed_file_format_.28.2A.gmt.29)
```

---

请将上述内容复制替换到 README.md 文件中。

**内容总结：**

1. **GMT 格式** — 每行 Tab 分隔：`基因集名称\t描述\t基因1\t基因2\t...`
2. **从 eggnog-mapper 构建 GMT** — 读取 `emapper.annotations` 文件，提取 `query` 和 `GOs` 列，将每个 GO term 映射到基因列表，写入 GMT
3. **gseapy 使用** — 提供两种方式：直接读 GMT 文件或传入 Python 字典
4. **常见问题** — 基因 ID 类型匹配、Tab 分隔符验证等