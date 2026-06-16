import os
# Set before importing other libraries that require OpenBLAS
os.environ["OPENBLAS_NUM_THREADS"] = "10"


from samap.mapping import SAMAP
from samap.analysis import (get_mapping_scores, GenePairFinder,
                            sankey_plot, chord_plot, CellTypeTriangles, 
                            ParalogSubstitutions, FunctionalEnrichment,
                            convert_eggnog_to_homologs, GeneTriangles)
from samalg import SAM
import pandas as pd
import scanpy as sc
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scanpy.external as sce
import scipy.sparse
from samalg import SAM #import SAM

import sys
species = sys.argv[1]
keys = sys.argv[2]

species = species.split(',')
keys = keys.split(',')

paths=[f"./SAMap/tmp/{s}.pkl" for s in species]

print(species, paths, keys)

cluster_key = {}
for name, key in zip(species, keys):
    cluster_key[name] = key
    
print(cluster_key)

neigh_from_keys={}
for name in species:
    neigh_from_keys[name] = True

print(neigh_from_keys)

# Load processed SAM
sams = {}
for name, file in zip(species, paths):
    sam = SAM()
    sam.load(file)
    sams[name] = sam

print(sams.keys())  # dict_keys(['At', 'Sp'])

sm = SAMAP(
    sams,
    f_maps = './SAMap/tmp/maps/',
    keys=cluster_key
)

# run the SAMap algorithm using the run function.
sm.run(pairwise=True, neigh_from_keys=neigh_from_keys)

samap = sm.samap

D, MappingTable = get_mapping_scores(sm, cluster_key, n_top = 0)

# D.to_csv("celltype_relationship.csv")
MappingTable.to_csv("./SAMap/SAMap_result/MappingTable.csv")

#sankey_plot(MappingTable, align_thr=0.05, species_order = sample[0].values)
sm.scatter()
plt.savefig("./SAMap/SAMap_result/Merge_UMAP.pdf")

gpf = GenePairFinder(sm,keys=cluster_key)
gene_pairs = gpf.find_all(align_thr=0.2)
gene_pairs.to_csv("./SAMap/SAMap_result/gene_pairs.csv")
adata=samap.adata
adata.obs['celltype']=samap.adata.obs[';'.join(keys) + '_mapping_scores']
adata.obsm['wPCA']=samap.adata.obsm['X_umap']

adata.write_h5ad(filename='./SAMap/SAMap_result/all.h5ad',compression="gzip")

import matplotlib.pyplot as plt

# 方法2：手动控制保存路径
fig, axs = plt.subplots(2, 1, figsize=(8, 12))
sc.pl.umap(adata, color='species', title='Colored by Species', 
           ax=axs[0], frameon=False, show=False)
sc.pl.umap(adata, color='celltype', title='Colored by Cell Type', 
           ax=axs[1], frameon=False, show=False)
plt.savefig('./SAMap/SAMap_result/umap_species_celltype.pdf', bbox_inches='tight', dpi=300)