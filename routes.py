import route_search_models
import random
import networkx as nx


def find_random_origin_destination_pairs(digraph, pairs_number):
    nodes = list(digraph.nodes())
    pairs = []
    while len(pairs) < pairs_number:
        source, destination = random.sample(nodes, k=2)
        if source == destination or digraph.has_edge(source, destination) or not nx.has_path(digraph, source, destination):
            continue
        pair = (source, destination)
        if pair not in pairs:
            pairs.append(pair)
    return pairs


def calculate_different_models_weights(digraph):
    d1 = route_search_models.distance_model(digraph)
    d2 = route_search_models.traffic_model(d1)
    d3 = route_search_models.social_model(d2)
    d4 = route_search_models.complexity_model(d3)
    d5 = route_search_models.combined_model(d4)
    d6 = route_search_models.least_time_without_traffic_model(d5)
    d7 = route_search_models.least_time_with_traffic_model(d6)

    return d7


def path_finder(digraph, model_number, source, destination):
    weight_map = {
        1: 'distance_weight',
        2: 'traffic_weight',
        3: 'social_weight',
        4: 'complexity_weight',
        5: 'combined_weight',
        6: 'least_time_without_traffic_weight',
        7: 'least_time_with_traffic_weight',
    }
    weight_string = weight_map.get(model_number, '')
    cost_string = weight_map.get(model_number, '')

    path = nx.dijkstra_path(digraph, source, destination, weight=cost_string)
    path_weights_sum = 0
    print('path weights: ')
    for n in range(len(path) - 1):
        weight = digraph.edges[path[n], path[n + 1]].get(weight_string, 0)
        path_weights_sum += weight
        print(weight)

    return path, path_weights_sum
