import itertools

import calliope
import click
import networkx as nx


STYLES = {
    "default": dict(fillcolor="#8b8b8b", fontcolor="#ffffff", style="filled"),
    # Tech and carrier nodes
    "carrier": dict(color="#8ea6f0"),
    "supply": dict(fillcolor="#267c2a", fontcolor="#ffffff", style="filled"),
    "storage": dict(fillcolor="#800080", fontcolor="#ffffff", style="filled"),
    "demand": dict(fillcolor="#ffd92f", fontcolor="#ffffff", style="filled"),
    "conversion": dict(fillcolor="#9e4a3d", fontcolor="#ffffff", style="filled"),
    "conversion_plus": dict(fillcolor="#dc5e4b", fontcolor="#ffffff", style="filled"),
    # Carrier edges
    "electricity": dict(color="#800080"),
    "heat": dict(color="#dc5e4b"),
}


def update_set(set_, item):
    if isinstance(item, list):
        set_.update(item)
    else:
        set_.add(item)
        
def techs_and_carriers_from_set(loc_tech_carriers_set):
    # loc::tech::carriers -> (locs, techs, carriers)
    split_set = loc_tech_carriers_set.to_index().str.split("::", expand=True)
    # transmission techs (tech:remote_loc) -> tech only
    techs = split_set.levels[1].str.split(":", expand=True).levels[0]
    
    carriers = split_set.levels[-1]
    
    return techs, carriers


def add_tech_edges(model, G, tech):
    carriers_in = set()
    for k, v in model._model_run.techs[tech].essentials.items():
        if "carrier_in" in k:
            update_set(carriers_in, v)

    carriers_out = set()
    for k, v in model._model_run.techs[tech].essentials.items():
        if "carrier_out" in k:
            update_set(carriers_out, v)

    for c in carriers_in:
        if c in STYLES:
            G.add_edge(c, tech, **STYLES[c])
        else:
            G.add_edge(c, tech)

    for c in carriers_out:
        if c in STYLES:
            G.add_edge(tech, c, **STYLES[c])
        else:
            G.add_edge(tech, c)


@click.command()
@click.argument("model_file")
@click.argument("out_file")
@click.option("--scenario", "-s", type=str, default=None)
def model_to_graph(model_file, out_file, scenario):
    model = calliope.Model(model_file, scenario=scenario)

    # Build set of all carriers and list of all techs

    techs_prod, carriers_prod = techs_and_carriers_from_set(model._model_data.loc_tech_carriers_prod)
    techs_con, carriers_con = techs_and_carriers_from_set(model._model_data.loc_tech_carriers_con)
    techs = techs_prod.union(techs_con)
    carriers = carriers_prod.union(carriers_con)

    # then create an undirected graph and add all items
    # from both of these lists as nodes

    G = nx.DiGraph()

    G.add_nodes_from(carriers, kind="carrier", **STYLES["carrier"])

    for tech in techs:
        tech_kind = model._model_run.techs[tech].inheritance[-1]
        G.add_node(tech, kind=tech_kind, **STYLES.get(tech_kind, STYLES["default"]))

    for tech in techs:
        add_tech_edges(model, G, tech)

    nx.drawing.nx_pydot.write_dot(G, out_file)


if __name__ == "__main__":
    model_to_graph()
