import scanpy as sc
import pandas as pd
import sys

file_paths = sys.argv[1]
none_raw_lst = sys.argv[2]


sample = pd.read_table(file_paths, sep='\t',header=None)

raw=[]
with open(none_raw_lst,'r') as f:
	for line in f:
             elem = ''.join(line.strip('\n').split(','))
             raw.append(elem)


for i in range(0,len(sample)):
    adata = sc.read_h5ad(sample.iat[i,1])
    adata.obs['species'] = sample.iat[i,0]
    sc.pp.calculate_qc_metrics(adata,inplace=True)
    if (sample.iat[i,0] in raw):
        adata.X=adata.layers["counts"]
        adata.obs['celltype']=adata.obs['leiden_res_0.50']
    #adata.dict['_raw'].dict['_var'] = adata.dict['_raw'].dict['_var'].rename(columns={'_index': 'features'})
    adata.obs['celltypes']= sample.iat[i,0] + "_" + adata.obs['celltype'].astype(str)
    del(adata.raw)
    #del(adata.var['_index'])
    adata.write_h5ad(filename=sample.iat[i,0]+'.h5ad',compression="gzip")
   

 
