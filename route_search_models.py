# Model Number 1
def distance_model(digraph):
    for u, v, data in digraph.edges(data=True):
        weight = data['distance']
        data['distance_weight'] = weight
    return digraph


# Model Number 2
def traffic_model(digraph):
    max_traffic = max(data['traffic'] for _, _, data in digraph.edges(data=True))
    for node1, node2, data in digraph.edges(data=True):
        weight = data['traffic'] / max_traffic
        digraph.edges[node1, node2]['traffic_weight'] = weight
    return digraph


# Model Number 3
def social_model(digraph):
    MAX_SOCIAL_WEIGHT = 6
    for (node1, node2, data) in digraph.edges(data=True):
        weight = data['way_type_num'] / MAX_SOCIAL_WEIGHT
        data['social_weight'] = weight
    return digraph


# Model Number 4
def complexity_model(digraph):
    distance_list = []
    branch_list = []
    deviation_list = []
    instruction_equivalent_list = []
    instruction_complexity_list = []
    landmark_list = []
    for (node1, node2, data) in digraph.edges(data=True):
        distance_list.append(data['distance'])
        branch_list.append(digraph.nodes[node1]['numOfBranches'])
        deviation_list.append(digraph.nodes[node1]['avgDeviation'])
        instruction_complexity_list.append(digraph.nodes[node1]['instComplexity'])
        instruction_equivalent_list.append(digraph.nodes[node1]['instEquivalent'])
        landmark_list.append(digraph.nodes[node1]['landmark'])

    max_distance = max(distance_list)
    max_branch = max(branch_list)
    max_deviation = max(deviation_list)
    max_instruction_equivalent = max(instruction_equivalent_list)
    max_instruction_complexity = max(instruction_complexity_list)
    max_landmark = max(landmark_list)

    model_parameters_num = 6
    for (node1, node2, data) in digraph.edges(data=True):
        weight_sum = (1 - (data['distance'] / max_distance)) + \
                     (digraph.nodes[node1]['numOfBranches'] / max_branch) + \
                     (digraph.nodes[node1]['avgDeviation'] / max_deviation) + \
                     (digraph.nodes[node1]['instEquivalent'] / max_instruction_equivalent) + \
                     (digraph.nodes[node1]['instComplexity'] / max_instruction_complexity) + \
                     (1 - (digraph.nodes[node1]['landmark'] / max_landmark))

        digraph.edges[node1, node2]['complexity_weight'] = weight_sum / model_parameters_num

    return digraph


# Model Number 5
def combined_model(digraph):
    distance_list = [data['distance'] for _, _, data in digraph.edges(data=True)]
    branch_list = [digraph.node[node1]['numOfBranches'] for node1, _, _ in digraph.edges(data=True)]
    deviation_list = [digraph.node[node1]['avgDeviation'] for node1, _, _ in digraph.edges(data=True)]
    instruction_equivalent_list = [digraph.node[node1]['instEquivalent'] for node1, _, _ in digraph.edges(data=True)]
    instruction_complexity_list = [digraph.node[node1]['instComplexity'] for node1, _, _ in digraph.edges(data=True)]
    landmark_list = [digraph.node[node1]['landmark'] for node1, _, _ in digraph.edges(data=True)]
    traffic_list = [data['traffic'] for _, _, data in digraph.edges(data=True)]

    max_distance = max(distance_list)
    max_branch = max(branch_list)
    max_deviation = max(deviation_list)
    max_instruction_equivalent = max(instruction_equivalent_list)
    max_instruction_complexity = max(instruction_complexity_list)
    max_landmark = max(landmark_list)
    max_traffic = max(traffic_list)
    max_social_weight = 6

    w_c = 1 / 3
    complexity_model_parameters_num = 6
    w_s = 1 / 3
    social_model_parameters_num = 1
    w_t = 1 / 3
    traffic_model_parameters_num = 1

    for node1, node2, data in digraph.edges(data=True):
        complexity_model_temp = (1 - (data['distance'] / max_distance)) + \
                                (digraph.node[node1]['numOfBranches'] / max_branch) + \
                                (digraph.node[node1]['avgDeviation'] / max_deviation) + \
                                (digraph.node[node1]['instEquivalent'] / max_instruction_equivalent) + \
                                (digraph.node[node1]['instComplexity'] / max_instruction_complexity) + \
                                (1 - (digraph.node[node1]['landmark'] / max_landmark))
        complexity_model = complexity_model_temp / complexity_model_parameters_num

        social_model_temp = (data['way_type_num'] / max_social_weight)
        social_model = social_model_temp / social_model_parameters_num

        traffic_model_temp = (data['traffic'] / max_traffic)
        traffic_model = traffic_model_temp / traffic_model_parameters_num

        weight = ((w_c * complexity_model) + (w_s * social_model) + (w_t * traffic_model)) / (w_c + w_s + w_t)
        digraph.edges[node1, node2]['combined_weight'] = weight

    return digraph


# Model Number 6
def least_time_without_traffic_model(digraph):
    for edge in digraph.edges(data=True):
        weight = edge[2]['no_traffic_time']
        edge[2]['least_time_without_traffic_weight'] = weight
    return digraph


# Model Number 7
def least_time_with_traffic_model(digraph):
    for edge in digraph.edges(data=True):
        weight = edge[2]['traffic_time']
        edge[2]['least_time_with_traffic_weight'] = weight
    return digraph
