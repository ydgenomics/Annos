
- 去掉adata.raw避免一些问题
- SAMap要求输入的是原始数据即.X的矩阵为整数矩阵，但是考虑到有些公共数据缺少了原始数据，可以取消里面的sam.preprocess_data()
- adata.X必须为稀疏矩阵

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