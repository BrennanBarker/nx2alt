"""Translating `networkx` graphs into the data structure preferred by `altair.`

example:
Given a networkx graph G and any networkx layout function, e.g. `spring_layout`

```python
from nx2alt import base_layers, altair_network_data
node_base, edge_base = base_layers(*altair_network_data(G, spring_layout))

edges = edge_base.mark_line(color='gray')
nodes = node_base.mark_circle(size=300)
labels = node_base.mark_text().encode(text='node_id')

edges + nodes + labels
```

"""

import networkx as nx
import pandas as pd
import altair as alt


def altair_node_data(G, pos=None):
    
    node_data = {k: dict(v, **{'node_id': k}) for k,v in G.nodes.data()}
    
    node_df = (pd.DataFrame.from_dict(node_data, orient='index')
               .reset_index(drop=True))
    
    if pos:
        node_df['x'] = node_df['node_id'].apply(lambda n: pos[n][0])
        node_df['y'] = node_df['node_id'].apply(lambda n: pos[n][1])
    
    return node_df

def altair_edge_data(G):
    edge_df = (
        nx.to_pandas_edgelist(G).reset_index()
        .rename(columns={'index': 'edge_id'})
    )
    
    ids= [c for c in edge_df.columns if c not in {'source', 'target'}]

    return edge_df.melt(id_vars=ids, var_name='end', value_name='node_id')

def altair_network_data(G, layout=None, **kwargs):
    if not callable(layout): pos = layout 
    else: pos = layout(G, **kwargs)
    return altair_node_data(G, pos), altair_edge_data(G)

def base_layers(node_data, edge_data):
    x,y = alt.X('x:Q', axis=None), alt.Y('y:Q', axis=None)
    lookup = alt.LookupData(data=node_data, key='node_id', fields=['x', 'y'])

    node_base = alt.Chart(node_data).encode(x=x, y=y)
    edge_base = (
        alt.Chart(edge_data)
        .encode(x=x, y=y, detail='edge_id')  # `detail` for one line per edge
        .transform_lookup(
            lookup='node_id',
            from_=lookup,)
    )
    return node_base, edge_base
