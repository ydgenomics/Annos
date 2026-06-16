### Date: 260310

import pandas as pd
import sys
import plotly.graph_objects as go
from operator import itemgetter
import matplotlib.pyplot as plt
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Generate a Sankey plot from metaNeighbor results.")
parser.add_argument('--path', type=str, default="/data/work/Single-Cell-Pipeline/output/Similarity/cotton_metaNeighbor.csv", help='Path to the metaNeighbor CSV file')
parser.add_argument('--seq', type=str, default="s1,s2", help='Order split with ,')
parser.add_argument('--slimit', type=float, default=0.8, help='Similarity limit threshold')

args = parser.parse_args()
path = args.path
seq = args.seq
slimit = args.slimit

limit = float(slimit)
MT = pd.read_table(path, sep=',', header=0)
MT.head()

def sanky_plot(MT,seq,limit):
    sequences = seq.split(',')
    # with open(seq, 'r') as f:
    #     for line in f:
    #         sequences.extend(line.strip('\n').split('|'))
    temp=MT.melt(id_vars=['Unnamed: 0'])
    temp0=temp
    ##deleting rows not satisfy the sequence    
    temp1=temp['Unnamed: 0'].str.split(pat="|",n=-1,expand=True)[0]
    temp2=temp['variable'].str.split(pat="|",n=-1,expand=True)[0]
    if not set(sequences) & set(temp1.unique()):   # 完全无交集
        sequences = temp1.unique().tolist()
    index0=dict(zip(sequences, range(len(sequences))))
    source0=list(itemgetter(*temp1.values)(index0))
    target0=list(itemgetter(*temp2.values)(index0))
    select=[source0[i] < target0[i] for i in range(len(source0))]
    temp1=temp0.loc[select]
    temp=temp1[temp1.value>limit]
    types=MT['Unnamed: 0'].values
    indexs=dict(zip(types, range(len(types))))
    colors=plt.cm.plasma(np.linspace(0, 1, len(indexs)))
    fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = types,
    ),
    link = dict(
      source = list(itemgetter(*temp['Unnamed: 0'].values)(indexs)), # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = list(itemgetter(*temp['variable'].values)(indexs)),
      value = list(temp['value'].values)
    ))])
    return fig

if __name__ == '__main__':
    fig=sanky_plot(MT,seq,limit)
    name=path.split("_metaNeighbor.csv",1)[0]
    fig.write_html(name + "_sanky.html")