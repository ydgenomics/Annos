from samap.mapping import SAMAP
from samap.analysis import (get_mapping_scores, GenePairFinder,
                            sankey_plot, chord_plot, CellTypeTriangles, 
                            ParalogSubstitutions, FunctionalEnrichment,
                            convert_eggnog_to_homologs, GeneTriangles)
from samalg import SAM
import pandas as pd
import matplotlib.pyplot as plt
import sys
import anndata as ad
#import click

#@click.command()
#@click.argument("maps", type=click.Path(exists=True))
#@click.argument("meta", type=click.Path(exists=True))
#@click.argument("out_h5ad", type=click.Path(exists=False), default=None)
#@click.argument("out_umap", type=click.Path(exists=False), default=None)
#@click.option('--batch_key', type=str, default=None, help="Batch key in identifying HVG and harmony integration")
#@click.option('--species_key', type=str, default=None, help="Species key to distinguish species")
#@click.option('--cluster_key', type=str, default=None, help="Cluster key in species one to use as labels to transfer to species two")

maps=sys.argv[1]
meta=sys.argv[2]


sample=pd.read_table(meta,sep='\t', header=None)
filenames={}
for i in range(0,len(sample)):
    filenames[sample.iat[i,0]]=sample.iat[i,1]

keys = {}
for i in range(0,len(sample)):
    keys[sample.iat[i,0]]="celltype"

neigh_from_keys={}
for i in range(0,len(sample)):
    neigh_from_keys[sample.iat[i,0]]=True


sm = SAMAP(filenames,f_maps = maps,keys=keys)
sm.run(pairwise=True,neigh_from_keys=neigh_from_keys)
samap = sm.samap


D,MappingTable = get_mapping_scores(sm,keys,n_top = 0)
D.to_csv("celltype_relationship.csv")
MappingTable.to_csv("MappingTable.csv")

#sankey_plot(MappingTable, align_thr=0.05, species_order = sample[0].values)

sm.scatter()
plt.savefig("Merge_UMAP.pdf")

gpf = GenePairFinder(sm,keys=keys)
gene_pairs = gpf.find_all(align_thr=0.2)
gene_pairs.to_csv("gene_pairs.csv")
adata=samap.adata
adata.obs['celltype']=samap.adata.obs['celltype;celltype_mapping_scores']
adata.obsm['wPCA']=samap.adata.obsm['X_umap']

adata.write_h5ad(filename='all.h5ad',compression="gzip")

#import pickle
#pickle.dump(sm, open("all.pkl", 'wb'))








