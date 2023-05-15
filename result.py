from routes import path_finder
import csv

headers = [
    "origin", "destination", "least_distance_norm", "traffic_for_least_distance_avg",
    "complexity_for_least_distance_avg",
    "c_c_without_traffic_for_least_distance_avg", "c_c_with_traffic_for_least_distance_avg",
    "distance_for_least_traffic_norm", "least_traffic_avg", "complexity_for_least_traffic_avg",
    "c_c_without_traffic_for_least_traffic_avg", "c_c_with_traffic_for_least_traffic_avg",
    "distance_for_most_social_norm", "traffic_for_most_social_avg", "complexity_for_most_social_avg",
    "c_c_without_traffic_for_most_social_avg", "c_c_with_traffic_for_most_social_avg",
    "distance_for_least_complexity_norm", "traffic_for_least_complexity_avg", "least_complexity_avg",
    "distance_for_least_combined_norm", "traffic_for_least_combined_avg",
    "complexity_for_least_combined_avg",
    "c_c_with_traffic_for_least_combined_avg",
    "complexity_for_least_time_no_traffic_avg",
    "complexity_for_least_time_with_traffic_avg"
]


def calculate_result(digraph, origin_destination_list, file_name):
    with open(f'{file_name}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for origin, destination in origin_destination_list:
            path_1, least_distance = path_finder(digraph, 1, origin, destination)
            least_distance_norm, traffic_for_least_distance_avg, complexity_for_least_distance_avg, \
                c_c_without_traffic_for_least_distance_avg, c_c_with_traffic_for_least_distance_avg = \
                least_distance_calculations(digraph, path_1)

            path_2, least_traffic = path_finder(digraph, 2, origin, destination)
            distance_for_least_traffic_norm, least_traffic_avg, complexity_for_least_traffic_avg, \
                c_c_without_traffic_for_least_traffic_avg, c_c_with_traffic_for_least_traffic_avg = \
                least_traffic_calculation(digraph, path_2, least_traffic, least_distance)

            path_3, most_social = path_finder(digraph, 3, origin, destination)
            distance_for_most_social_norm, traffic_for_most_social_avg, complexity_for_most_social_avg, \
                c_c_without_traffic_for_most_social_avg, c_c_with_traffic_for_most_social_avg = \
                most_social_calculation(digraph, path_3, least_distance)

            path_4, least_complexity = path_finder(digraph, 4, origin, destination)
            distance_for_least_complexity_norm, traffic_for_least_complexity_avg, least_complexity_avg = \
                least_complexity_calculation(digraph, path_4, least_complexity, least_distance)

            path_5, least_combined = path_finder(digraph, 5, origin, destination)
            distance_for_least_combined_norm, traffic_for_least_combined_avg, complexity_for_least_combined_avg, \
                complexity_for_least_combined_avg, c_c_with_traffic_for_least_combined_avg = \
                least_combined_calculation(digraph, path_5, least_distance)

            path_6, least_time_no_traffic = path_finder(digraph, 6, origin, destination)
            complexity_for_least_time_no_traffic_avg = least_time_no_traffic_calculation(digraph, path_6)

            path_7, least_time_with_traffic = path_finder(digraph, 7, origin, destination)
            complexity_for_least_time_with_traffic_avg = least_time_with_traffic_calculation(digraph, path_7)

            writer.writerow([origin, destination,
                             least_distance_norm, traffic_for_least_distance_avg, complexity_for_least_distance_avg,
                             c_c_without_traffic_for_least_distance_avg, c_c_with_traffic_for_least_distance_avg,
                             distance_for_least_traffic_norm, least_traffic_avg, complexity_for_least_traffic_avg,
                             c_c_without_traffic_for_least_traffic_avg, c_c_with_traffic_for_least_traffic_avg,
                             distance_for_most_social_norm, traffic_for_most_social_avg, complexity_for_most_social_avg,
                             c_c_without_traffic_for_most_social_avg, c_c_with_traffic_for_most_social_avg,
                             distance_for_least_complexity_norm, traffic_for_least_complexity_avg, least_complexity_avg,
                             distance_for_least_combined_norm, traffic_for_least_combined_avg,
                             complexity_for_least_combined_avg,
                             complexity_for_least_combined_avg, c_c_with_traffic_for_least_combined_avg,
                             complexity_for_least_time_no_traffic_avg,
                             complexity_for_least_time_with_traffic_avg])


def least_distance_calculations(digraph, path, least_distance):
    path_num_of_edges = len(path)
    traffic_for_least_distance = 0
    social_for_least_distance = 0
    complexity_for_least_distance = 0
    combined_for_least_distance = 0
    c_c_without_traffic_for_least_distance = 0
    c_c_with_traffic_for_least_distance = 0
    c_s_without_traffic_for_least_distance = 0
    c_s_with_traffic_for_least_distance = 0
    for n in range(path_num_of_edges - 1):
        traffic_for_least_distance += digraph.edges[path[n], path[n + 1]]['traffic_weight']
        social_for_least_distance += digraph.edges[path[n], path[n + 1]]['social_weight']
        complexity_for_least_distance += digraph.edges[path[n], path[n + 1]]['complexity_weight']
        combined_for_least_distance += digraph.edges[path[n], path[n + 1]]['combined_weight']
        c_c_without_traffic_for_least_distance += digraph.edges[path[n], path[n + 1]]['complexity_weight']
        c_c_with_traffic_for_least_distance += digraph.edges[path[n], path[n + 1]]['complexity_weight']
        c_s_without_traffic_for_least_distance += digraph.edges[path[n], path[n + 1]]['social_weight']
        c_s_with_traffic_for_least_distance += digraph.edges[path[n], path[n + 1]]['social_weight']
    least_distance_norm = least_distance / least_distance
    traffic_for_least_distance_avg = traffic_for_least_distance / path_num_of_edges
    complexity_for_least_distance_avg = complexity_for_least_distance / path_num_of_edges
    c_c_without_traffic_for_least_distance_avg = c_c_without_traffic_for_least_distance / path_num_of_edges
    c_c_with_traffic_for_least_distance_avg = c_c_without_traffic_for_least_distance / path_num_of_edges
    return (least_distance_norm, traffic_for_least_distance_avg, complexity_for_least_distance_avg,
            c_c_without_traffic_for_least_distance_avg, c_c_with_traffic_for_least_distance_avg)


def least_traffic_calculation(digraph, path_2, least_traffic, least_distance):
    path_2_num_of_edges = len(path_2)
    distance_for_least_traffic = 0
    social_for_least_traffic = 0
    complexity_for_least_traffic = 0
    combined_for_least_traffic = 0
    c_c_without_traffic_for_least_traffic = 0
    c_c_with_traffic_for_least_traffic = 0
    c_s_without_traffic_for_least_traffic = 0
    c_s_with_traffic_for_least_traffic = 0
    for n in range(path_2_num_of_edges - 1):
        distance_for_least_traffic += digraph.edges[path_2[n], path_2[n + 1]]['distance_weight']
        social_for_least_traffic += digraph.edges[path_2[n], path_2[n + 1]]['social_weight']
        complexity_for_least_traffic += digraph.edges[path_2[n], path_2[n + 1]]['complexity_weight']
        combined_for_least_traffic += digraph.edges[path_2[n], path_2[n + 1]]['combined_weight']
        c_c_without_traffic_for_least_traffic += digraph.edges[path_2[n], path_2[n + 1]]['complexity_weight']
        c_c_with_traffic_for_least_traffic += digraph.edges[path_2[n], path_2[n + 1]]['complexity_weight']
        c_s_without_traffic_for_least_traffic += digraph.edges[path_2[n], path_2[n + 1]]['social_weight']
        c_s_with_traffic_for_least_traffic += digraph.edges[path_2[n], path_2[n + 1]]['social_weight']
    distance_for_least_traffic_norm = distance_for_least_traffic / least_distance
    least_traffic_avg = least_traffic / path_2_num_of_edges
    complexity_for_least_traffic_avg = complexity_for_least_traffic / path_2_num_of_edges
    c_c_without_traffic_for_least_traffic_avg = c_c_without_traffic_for_least_traffic / path_2_num_of_edges
    c_c_with_traffic_for_least_traffic_avg = c_c_with_traffic_for_least_traffic / path_2_num_of_edges
    return (distance_for_least_traffic_norm, least_traffic_avg, complexity_for_least_traffic_avg,
            c_c_without_traffic_for_least_traffic_avg, c_c_with_traffic_for_least_traffic_avg)


def most_social_calculation(digraph, path_3, least_distance):
    path_3_num_of_edges = len(path_3)
    distance_for_most_social = 0
    traffic_for_most_social = 0
    complexity_for_most_social = 0
    combined_for_most_social = 0
    c_c_without_traffic_for_most_social = 0
    c_c_with_traffic_for_most_social = 0
    c_s_without_traffic_for_most_social = 0
    c_s_with_traffic_for_most_social = 0
    for n in range(path_3_num_of_edges - 1):
        distance_for_most_social += digraph.edges[path_3[n], path_3[n + 1]]['distance_weight']
        traffic_for_most_social += digraph.edges[path_3[n], path_3[n + 1]]['traffic_weight']
        complexity_for_most_social += digraph.edges[path_3[n], path_3[n + 1]]['complexity_weight']
        combined_for_most_social += digraph.edges[path_3[n], path_3[n + 1]]['combined_weight']
        c_c_without_traffic_for_most_social += digraph.edges[path_3[n], path_3[n + 1]]['complexity_weight']
        c_c_with_traffic_for_most_social += digraph.edges[path_3[n], path_3[n + 1]]['complexity_weight']
        c_s_without_traffic_for_most_social += digraph.edges[path_3[n], path_3[n + 1]]['social_weight']
        c_s_with_traffic_for_most_social += digraph.edges[path_3[n], path_3[n + 1]]['social_weight']
    distance_for_most_social_norm = distance_for_most_social / least_distance
    traffic_for_most_social_avg = traffic_for_most_social / path_3_num_of_edges
    complexity_for_most_social_avg = complexity_for_most_social / path_3_num_of_edges
    c_c_without_traffic_for_most_social_avg = c_c_without_traffic_for_most_social / path_3_num_of_edges
    c_c_with_traffic_for_most_social_avg = c_c_with_traffic_for_most_social / path_3_num_of_edges
    return (distance_for_most_social_norm, traffic_for_most_social_avg, complexity_for_most_social_avg,
            c_c_without_traffic_for_most_social_avg, c_c_with_traffic_for_most_social_avg)


def least_complexity_calculation(digraph, path_4, least_complexity, least_distance):
    path_4_num_of_edges = len(path_4)
    distance_for_least_complexity = 0
    traffic_for_least_complexity = 0
    social_for_least_complexity = 0
    combined_for_least_complexity = 0
    for n in range(path_4_num_of_edges - 1):
        distance_for_least_complexity += digraph.edges[path_4[n], path_4[n + 1]]['distance_weight']
        traffic_for_least_complexity += digraph.edges[path_4[n], path_4[n + 1]]['traffic_weight']
        social_for_least_complexity += digraph.edges[path_4[n], path_4[n + 1]]['social_weight']
        combined_for_least_complexity += digraph.edges[path_4[n], path_4[n + 1]]['combined_weight']
    distance_for_least_complexity_norm = distance_for_least_complexity / least_distance
    traffic_for_least_complexity_avg = traffic_for_least_complexity / path_4_num_of_edges
    least_complexity_avg = least_complexity / path_4_num_of_edges
    return distance_for_least_complexity_norm, traffic_for_least_complexity_avg, least_complexity_avg


def least_combined_calculation(digraph, path_5, least_distance):
    path_7_num_of_edges = len(path_5)
    distance_for_least_combined = 0
    traffic_for_least_combined = 0
    social_for_least_combined = 0
    complexity_for_least_combined = 0
    c_c_without_traffic_for_least_combined = 0
    c_c_with_traffic_for_least_combined = 0
    c_s_without_traffic_for_least_combined = 0
    c_s_with_traffic_for_least_combined = 0
    for n in range(path_7_num_of_edges - 1):
        distance_for_least_combined += digraph.edges[path_5[n], path_5[n + 1]]['distance_weight']
        traffic_for_least_combined += digraph.edges[path_5[n], path_5[n + 1]]['traffic_weight']
        social_for_least_combined += digraph.edges[path_5[n], path_5[n + 1]]['social_weight']
        complexity_for_least_combined += digraph.edges[path_5[n], path_5[n + 1]]['complexity_weight']
        c_c_without_traffic_for_least_combined += digraph.edges[path_5[n], path_5[n + 1]]['complexity_weight']
        c_c_with_traffic_for_least_combined += digraph.edges[path_5[n], path_5[n + 1]]['complexity_weight']
        c_s_without_traffic_for_least_combined += digraph.edges[path_5[n], path_5[n + 1]]['social_weight']
        c_s_with_traffic_for_least_combined += digraph.edges[path_5[n], path_5[n + 1]]['social_weight']
    distance_for_least_combined_norm = distance_for_least_combined / least_distance
    traffic_for_least_combined_avg = traffic_for_least_combined / path_7_num_of_edges
    complexity_for_least_combined_avg = complexity_for_least_combined / path_7_num_of_edges
    complexity_for_least_combined_avg = c_c_without_traffic_for_least_combined / path_7_num_of_edges
    c_c_with_traffic_for_least_combined_avg = c_c_with_traffic_for_least_combined / path_7_num_of_edges
    return (distance_for_least_combined_norm, traffic_for_least_combined_avg, complexity_for_least_combined_avg,
            complexity_for_least_combined_avg, c_c_with_traffic_for_least_combined_avg)


def least_time_no_traffic_calculation(digraph, path_6):
    path_6_num_of_edges = len(path_6)
    social_for_least_time_no_traffic = 0
    complexity_for_least_time_no_traffic = 0
    for n in range(path_6_num_of_edges - 1):
        social_for_least_time_no_traffic += digraph.edges[path_6[n], path_6[n + 1]]['social_weight']
        complexity_for_least_time_no_traffic += digraph.edges[path_6[n], path_6[n + 1]]['complexity_weight']
    complexity_for_least_time_no_traffic_avg = complexity_for_least_time_no_traffic / path_6_num_of_edges
    return complexity_for_least_time_no_traffic_avg


def least_time_with_traffic_calculation(digraph, path_7):
    path_7_num_of_edges = len(path_7)
    social_for_least_time_with_traffic = 0
    complexity_for_least_time_with_traffic = 0
    for n in range(path_7_num_of_edges - 1):
        social_for_least_time_with_traffic += digraph.edges[path_7[n], path_7[n + 1]]['social_weight']
        complexity_for_least_time_with_traffic += digraph.edges[path_7[n], path_7[n + 1]]['complexity_weight']
    complexity_for_least_time_with_traffic_avg = complexity_for_least_time_with_traffic / path_7_num_of_edges
    return complexity_for_least_time_with_traffic_avg
