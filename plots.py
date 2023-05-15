import networkx as nx
import matplotlib.pyplot as plt


def plot_path_graph(digraph, path, plot_name):
    positions = {n_id: (digraph.nodes[n_id]['lon'] * 1e7, digraph.nodes[n_id]['lat'] * 1e7) for n_id in digraph.nodes()}
    nodes_color = ['none' if n_id not in path else 'none' for n_id in digraph.nodes()]
    path_edges = [(path[n], path[n+1]) for n in range(len(path)-1)]
    edges_color = ['r' if e in path_edges else 'k' for e in digraph.edges()]
    fig, ax = plt.subplots(figsize=(8, 8))
    nx.draw_networkx(digraph, positions, node_color=nodes_color, node_size=1000, edge_color=edges_color,
                     width=5, arrowsize=20, ax=ax)
    fig.savefig(plot_name, format="PNG")
    plt.close(fig)


def plot_graph(digraph, plot_name):
    positions = {n_id: (digraph.nodes[n_id]['lon'] * 1e7, digraph.nodes[n_id]['lat'] * 1e7) for n_id in digraph.nodes()}
    nodes_color = 'none'
    edges_color = 'k'
    fig, ax = plt.subplots(figsize=(8, 8))
    nx.draw_networkx(digraph, positions, node_color=nodes_color, node_size=300, edge_color=edges_color,
                     width=5, arrowsize=20, ax=ax)
    fig.savefig(plot_name, format="PNG")
    plt.close(fig)


def plot_graph_with_details(digraph, plot_name):
    positions = {n_id: (digraph.nodes[n_id]['lon'] * 1e7, digraph.nodes[n_id]['lat'] * 1e7) for n_id in digraph.nodes()}
    nodes_color = ['none']
    traffic_severe_edges = [(u, v) for u, v, d in digraph.edges(data=True) if d['traffic'] >= 0.7]
    traffic_moderate_edges = [(u, v) for u, v, d in digraph.edges(data=True) if 0.3 <= d['traffic'] < 0.7]
    traffic_slight_edges = [(u, v) for u, v, d in digraph.edges(data=True) if d['traffic'] < 0.3]
    edges_color = ['r' if e in traffic_severe_edges else 'y' if e in traffic_moderate_edges else 'g' for e in
                   digraph.edges()]
    high_important_edge_type = [(u, v) for u, v, d in digraph.edges(data=True) if d['way_type'] in {'motorway', 'trunk'}]
    middle_important_edge_type = [(u, v) for u, v, d in digraph.edges(data=True) if
                                  d['way_type'] in {'primary', 'secondary', 'tertiary'}]
    low_important_edge_type = [(u, v) for u, v, d in digraph.edges(data=True) if d['way_type'] == 'residential']
    edges_width = [50 if e in high_important_edge_type else 25 if e in middle_important_edge_type else 5 for e in
                   digraph.edges()]
    fig, ax = plt.subplots(figsize=(8, 8))
    nx.draw_networkx(digraph, positions, node_color=nodes_color, node_size=1000, edge_color=edges_color,
                     width=edges_width, arrowsize=20, ax=ax)
    fig.savefig(plot_name, format="PNG")
    plt.close(fig)
