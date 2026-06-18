



- 去掉adata.raw避免一些问题
- SAMap要求输入的是原始数据即.X的矩阵为整数矩阵，但是考虑到有些公共数据缺少了原始数据，可以取消里面的sam.preprocess_data()
- adata.X必须为稀疏矩阵
- 增加了随机抽样的参数，极大节约了运行时间（2个物种共2万细胞只要半个小时）

```
fB = f_maps + "{}{}/{}_to_{}.txt".format(id2, id1, id2, id1)
```
传入三个列表，物种名，文件地址，细胞类型或细胞群的键
species="At,Sp,Sl"
paths=""
keys="celltype,celltype,Celltype"
```shell
>>> filenames
{'At': 'at.h5ad', 'Sp': 'sp.h5ad'}
>>> keys = {}
>>> for i in range(0,len(sample)):
...     keys[sample.iat[i,0]]="celltype"
... 
>>> keys
{'At': 'celltype', 'Sp': 'celltype'}
>>> neigh_from_keys={}
>>> for i in range(0,len(sample)):
...     neigh_from_keys[sample.iat[i,0]]=True
... 
>>> neigh_from_keys
{'At': True, 'Sp': True}
>>> 
```

- [xuzhougeng/CrossSpeciesPlantShootAtlas/02_CrossSpeciesIntegration](https://github.com/xuzhougeng/CrossSpeciesPlantShootAtlas/tree/main/02_CrossSpeciesIntegration)
- https://github.com/atarashansky/SAMap

<details> <summary> cross-species-integration </summary>

- **整合方法SAMap——利用多对多的基因对应关系确定物种间的细胞近邻关系，迭代式把多个物种的UMAP图拉到共享嵌入空间**
  - 第一个模块，连接同源基因对的跨物种边构建一个基因-基因双向图，最初按蛋白质序列相似性加权
  - 第二个模块，SAMap利用基因-基因图将两个单细胞转录组数据集投影到一个联合的低维流形表示中
  - 根据这一表征，每个细胞的跨物种互邻关系被连接起来，从而将细胞图谱拼接在一起，然后利用联合流行计算出的同源基因之间的表达相关性被**重新加权**基因-基因同源图谱中的边，从而放宽了SAMap最初堆序列相似性的依赖。这个新的同源图被用作SAMap后续迭代的输入，该算法一直持续到跨物种映射在迭代之间没有显著变化为止
- **整合方法SATURN**
  - SATURN接收来自一个或多个物种的单细胞RNA测序数据集及这些物种中蛋白质的氨基酸序列作为输入
  - SATURN通过学习“跨物种功能基因群”（microgenes），即功能相关的物种内及物种间基因的组，将每个物种的基因映射到一个联合特征空间中
  - 在共享的红基因空间中，SATURN通过学习一个联合细胞嵌入空间来跨物种整合数据集，在该空间中，跨物种保守的细胞类型相互对齐
- **注意事项**
  - 基因存在的多种转录形式。表达矩阵是基因水平，因此需要一个基因只保留一个代表转录本
  - 小心你使用的注释文件，很有可能一些蛋白序列里面存在*，SAMap未必有问题，但是ESM计算蛋白语义会出错
  - SAMap运行速度跟细胞数目有关，如果运行时间太久，可以考虑抽样细胞/metacell
  - ESM与ProtTrek
- **Ref**
  - https://github.com/xuzhougeng/CrossSpeciesPlantShootAtlas/tree/main/02_CrossSpeciesIntegration
  - 

</details>