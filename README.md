# modelgraph

Requires graphviz:

```
conda install graphviz
```

Required python packages: calliope, networkx, pydot

How to use:

```
python modelgraph.py path/to/model.yaml model-graph.dot
dot -Gratio=0.66 -Tpdf model-graph.dot -o model-graph.pdf
```

To specify a scenario:

```
python modelgraph.py --scenario=my_scenario path/to/model.yaml model-graph.dot
```
