import urllib.request
from urllib.error import HTTPError
import xml.sax
import networkx as nx
from statistics import mean
import itertools
import pyproj
import requests
import random
import time


class Node:
    def __init__(self, node_id, lon, lat, is_decision_point):
        self.id = node_id
        self.lon = lon
        self.lat = lat
        self.tags = {}
        self.is_decision_point = is_decision_point


class Way:
    def __init__(self, way_id, osm):
        self.osm = osm
        self.id = way_id
        self.nds = []
        self.tags = {}


class OSM:
    def __init__(self, filename_or_stream):
        nodes = {}
        ways = {}

        class OSMHandler(xml.sax.ContentHandler):
            def setDocumentLocator(self, loc):
                pass

            def startDocument(self):
                pass

            def endDocument(self):
                pass

            def startElement(self, name, attrs):
                nonlocal nodes, ways
                if name == 'node':
                    self.curr_elem = Node(attrs['id'], float(attrs['lon']), float(attrs['lat']), False)
                elif name == 'way':
                    self.curr_elem = Way(attrs['id'], self)
                elif name == 'tag':
                    self.curr_elem.tags[attrs['k']] = attrs['v']
                elif name == 'nd':
                    self.curr_elem.nds.append(attrs['ref'])

            def endElement(self, name):
                nonlocal nodes, ways
                if name == 'node':
                    nodes[self.curr_elem.id] = self.curr_elem
                elif name == 'way':
                    ways[self.curr_elem.id] = self.curr_elem

            def characters(self, chars):
                pass

        xml.sax.parse(filename_or_stream, OSMHandler())

        self.nodes = nodes
        self.ways = ways

        counter = {}
        for way in self.ways.values():
            if 'highway' in way.tags:
                if way.tags['highway'] in ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential']:
                    for node_ref in way.nds:
                        if node_ref not in counter:
                            counter[node_ref] = 0
                        counter[node_ref] += 1
        intersections_ref = [node_ref for node_ref in counter if counter[node_ref] > 1]
        print(f'Number of Decision Points: {len(intersections_ref)}')
        print(f'Decision Points: {intersections_ref}')

        for node in self.nodes.values():
            if node.id in intersections_ref:
                node.is_decision_point = True


def download_osm(left, bottom, right, top):
    """ https://wiki.openstreetmap.org/wiki/Downloading_data#Construct_a_URL_for_the_HTTP_API """
    request = "http://api.openstreetmap.org/api/0.6/map?bbox=%f,%f,%f,%f" % (left, bottom, right, top)
    try:
        with urllib.request.urlopen(request) as fp:
            if fp.status != 200:
                raise HTTPError(fp.url, fp.status, fp.reason, fp.headers, None)
            return fp
    except HTTPError as e:
        print(f"HTTP Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def create_osm_decisionpoints_digraph(filename_or_stream):
    global G_with_traffic
    print('Start Digraph Creation ...')
    osm = OSM(filename_or_stream)
    G = nx.DiGraph()

    for w in osm.ways.values():
        if 'highway' in w.tags and w.tags['highway'] in {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential'}:
            w_dp = [n_id for n_id in w.nds if osm.nodes[n_id].isDP]
            if 'oneway' in w.tags:
                if w.tags['oneway'] == 'yes':
                    G.add_path(w_dp, id=w.id)
                else:
                    G.add_path(w_dp, id=w.id)
                    G.add_path(w_dp[::-1], id=w.id)
            else:
                G.add_path(w_dp, id=w.id)
                G.add_path(w_dp[::-1], id=w.id)
    print('Calculating Node Parameters ...')

    for DP_id in G.nodes():
        DP = osm.nodes[DP_id]
        neighbor_list = list(G.neighbors(DP_id)) + list(G.predecessors(DP_id))  # combine the two neighbor lists
        numOfBranches = len(neighbor_list)

        G.nodes[DP_id]['lat'] = DP.lat
        G.nodes[DP_id]['lon'] = DP.lon
        G.nodes[DP_id]['id'] = DP.id
        G.nodes[DP_id]['numOfBranches'] = numOfBranches

        deviation_list = []
        bearing_differences_list = []
        neighbor_distance_list = []

        if numOfBranches >= 2:
            for a, b in itertools.combinations(neighbor_list, 2):
                node_a, node_b = osm.nodes[a], osm.nodes[b]
                pointA, pointDP, pointB = [node_a.lat, node_a.lon], [DP.lat, DP.lon], [node_b.lat, node_b.lon]

                fwd_azimuth_DPA, _, distance_DPA = get_azimuth(pointDP, pointA)
                neighbor_distance_list.append(distance_DPA)

                fwd_azimuth_DPB, _, distance_DPB = get_azimuth(pointDP, pointB)
                neighbor_distance_list.append(distance_DPB)

                bearing = abs(fwd_azimuth_DPA - fwd_azimuth_DPB)
                bearing_differences_list.append(bearing)
                deviation_list.append(calculate_deviation(bearing))

                if G.has_edge(DP_id, a):
                    G.edges[DP_id, a]['bearing'] = fwd_azimuth_DPA
                    G.edges[DP_id, a]['distance'] = distance_DPA
                else:
                    G.edges[a, DP_id]['bearing'] = fwd_azimuth_DPA
                    G.edges[a, DP_id]['distance'] = distance_DPA

                if G.has_edge(DP_id, b):
                    G.edges[DP_id, b]['bearing'] = fwd_azimuth_DPB
                    G.edges[DP_id, b]['distance'] = distance_DPB
                else:
                    G.edges[b, DP_id]['bearing'] = fwd_azimuth_DPB
                    G.edges[b, DP_id]['distance'] = distance_DPB

        elif numOfBranches == 1:
            a = neighbor_list[0]
            node_a = osm.nodes[a]
            pointA, pointDP = [node_a.lat, node_a.lon], [DP.lat, DP.lon]
            fwd_azimuth_DPA, _, distance_DPA = get_azimuth(pointDP, pointA)
            neighbor_distance_list.append(distance_DPA)

            if G.has_edge(DP_id, a):
                G.edges[DP_id, a]['bearing'] = fwd_azimuth_DPA
                G.edges[DP_id, a]['distance'] = distance_DPA
            else:
                G.edges[a, DP_id]['bearing'] = fwd_azimuth_DPA
                G.edges[a, DP_id]['distance'] = distance_DPA

        G.nodes[DP_id]['avgDeviation'] = mean(deviation_list) if deviation_list else 0
        bearing_list = [
            G.edges[DP_id, neighbor]['bearing'] if G.has_edge(DP_id, neighbor) else G.edges[neighbor, DP_id]['bearing']
            for neighbor in neighbor_list]
        G.nodes[DP_id]['instComplexity'] = calculate_instruction_complexity(bearing_differences_list, numOfBranches)
        G.nodes[DP_id]['instEquivalent'] = calculate_instruction_equivalent(bearing_list)
        G.nodes[DP_id]['landmark'] = calculate_landmark(DP, neighbor_distance_list)

        print('Calculating edge parameters...')

        WAY_TYPE_LIST = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'residential']
        WAY_TYPE_SPEED_LIST = [100, 80, 60, 60, 50, 30]

        for (node1, node2) in G.edges():
            if 'distance' not in G.edges[node1, node2]:
                G.edges[node1, node2]['distance'] = G.edges[node2, node1]['distance']
                way_id = G.edges[node2, node1]['id']
                way = osm.ways[way_id]
                way_type = way.tags.get('highway', None)
                if way_type:
                    G.edges[node1, node2]['way_type'] = way_type
                    G.edges[node1, node2]['way_type_num'] = WAY_TYPE_LIST.index(way_type) + 1

            if 'bearing' in G.edges[node1, node2]:
                way_id = G.edges[node1, node2]['id']
                way = osm.ways[way_id]
                way_type = way.tags.get('highway', None)
                if way_type:
                    G.edges[node1, node2]['way_type'] = way_type
                    G.edges[node1, node2]['way_type_num'] = WAY_TYPE_LIST.index(way_type) + 1

        G_with_traffic = add_traffic_to_osm_decisionpoints_digraph(G)

        for (node1, node2) in G.edges():
            way_type_num = G.edges[node1, node2]['way_type_num']
            if way_type_num:
                speed = WAY_TYPE_SPEED_LIST[way_type_num - 1]
                distance = G.edges[node1, node2]['distance']
                time = distance / speed
                G.edges[node1, node2]['no_traffic_time'] = time

                traffic = G.edges[node1, node2]['traffic']
                speed_coefficient = 1
                if traffic < 0.3:
                    speed_coefficient = 1
                elif 0.3 <= traffic < 0.7:
                    speed_coefficient = 0.75
                else:
                    speed_coefficient = 0.4
                time_traffic = distance / (speed * speed_coefficient)
                G.edges[node1, node2]['traffic_time'] = time_traffic

    return G_with_traffic


def add_traffic_to_osm_decisionpoints_digraph(digraph):
    bfs = list(nx.edge_bfs(digraph))
    for node_start, node_next in bfs:
        queue = []
        if not digraph.has_edge(node_start, node_next):
            continue
        if 'traffic' in digraph.edges[node_start, node_next]:
            continue
        if not digraph.has_edge(node_next, node_start):
            continue
        rand = random.uniform(0, 1)
        digraph.edges[node_start, node_next]['traffic'] = rand
        print(f"Traffic is: {rand}")
        queue.append(node_next)
        while queue:
            node = queue.pop(0)
            for neighbor in digraph.neighbors(node):
                if not digraph.has_edge(node, neighbor):
                    continue
                if 'traffic' in digraph.edges[node, neighbor]:
                    continue
                digraph.edges[node, neighbor]['traffic'] = calculate_traffic(digraph, node, neighbor)
                print(f"Traffic for edge ({node}, {neighbor}) is: {digraph.edges[node, neighbor]['traffic']}")
                queue.append(neighbor)
    return digraph


def calculate_traffic(digraph, start_node, end_node):
    w1 = 1
    edge_type_num_max = 6
    edge_type_num = digraph.edges[start_node, end_node]['way_type_num']
    predecessors_list = list(digraph.predecessors(start_node))
    sum_traffic_predecessors = 0
    count_traffic_predecessors = 0
    avg_traffic_predecessors = 0
    for node in predecessors_list:
        if 'traffic' in digraph.edges[node, start_node]:
            sum_traffic_predecessors += digraph.edges[node, start_node]['traffic']
            count_traffic_predecessors += 1
    if count_traffic_predecessors:
        avg_traffic_predecessors = sum_traffic_predecessors / count_traffic_predecessors
    rand = random.uniform(0, 0.4)
    if edge_type_num in (4, 5, 6):
        traffic = abs(avg_traffic_predecessors - rand)
    else:
        traffic = min(0.90, avg_traffic_predecessors + rand)
    return traffic


def get_azimuth(point_a, point_b):
    lat1, lat2, long1, long2 = point_a[0], point_b[0], point_a[1], point_b[1]
    geodesic = pyproj.Geod(ellps='WGS84')
    fwd_azimuth, back_azimuth, distance = geodesic.inv(long1, lat1, long2, lat2)
    return fwd_azimuth, back_azimuth, distance


def calculate_deviation(bearing):
    if bearing <= 90:
        a = 90 - bearing
        return min(a, bearing)
    elif bearing <= 180:
        a = 180 - bearing
        b = bearing - 90
        return min(a, b)
    elif bearing <= 270:
        a = 270 - bearing
        b = bearing - 180
        return min(a, b)
    elif bearing <= 360:
        a = 360 - bearing
        b = bearing - 270
        return min(a, b)
    else:
        return 0


def calculate_instruction_equivalent(bearing_list):
    if bearing_list:
        zero_to_ninety = len([bearing for bearing in bearing_list if 0 < bearing < 90])
        ninety_to_oneeighty = len([bearing for bearing in bearing_list if 90 < bearing < 180])
        minus_ninety_to_zero = len([bearing for bearing in bearing_list if -90 < bearing < 0])
        minus_oneeighty_to_minus_ninety = len([bearing for bearing in bearing_list if -180 < bearing < -90])
        max_count = max(zero_to_ninety, ninety_to_oneeighty, minus_ninety_to_zero, minus_oneeighty_to_minus_ninety, 1)
        return max_count
    else:
        return 1


def calculate_instruction_complexity(bearing_differences_list, num_of_branches):
    if bearing_differences_list:
        complexity_list = []
        for bearing_diff in bearing_differences_list:
            if -10 <= bearing_diff <= 10:
                complexity_list.append(1)
            else:
                if num_of_branches == 3:
                    complexity_list.append(6)
                else:
                    complexity_list.append(5 + num_of_branches)
        return mean(complexity_list)
    else:
        return 0


def calculate_landmark(DP, neighbor_distance_list):
    global response
    AMENITY_TYPE_LIST = [
        'others', 'school', 'restaurant', 'police', 'park',
        'hotel', 'hospital', 'embassy', 'cinema', 'cafe', 'bank'
    ]

    W1 = 1
    W2 = 0

    if len(neighbor_distance_list) != 0:
        around_value = min(50, (max(neighbor_distance_list) * 1000) / 2)
    else:
        around_value = 50

    amenity_salience_list = []
    amenity_distance_list = []
    amenity_value = 0

    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """
        [out:json];
        (node["amenity"](around:{}, {}, {}); 
         way["amenity"](around:{}, {}, {});
         rel["amenity"](around:{}, {}, {});
        );
        out center;
        """.format(around_value, DP.lat, DP.lon, around_value, DP.lat, DP.lon, around_value, DP.lat, DP.lon)
    headers = {'referer': 'fateme_referer'}
    retry = True
    while retry:
        response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers)
        if response.ok and 'json' in response.headers.get('Content-Type'):
            retry = False
            print('landmark api: success')
            print(DP.id)
        else:
            print('landmark api: fail')
            print(DP.id)
            time.sleep(2)

    data = response.json()
    for element in data['elements']:
        if element['type'] == 'node' or 'center' in element:
            lon = element.get('lon', element['center']['lon'])
            lat = element.get('lat', element['center']['lat'])
            coords_1 = (lat, lon)
            coords_2 = (DP.lat, DP.lon)
            fwd_azimuth, back_azimuth, distance = get_azimuth(coords_1, coords_2)
            amenity_distance_list.append(distance)

            tags = element['tags']
            amenity_type = tags.get('amenity')
            if amenity_type in AMENITY_TYPE_LIST:
                amenity_salience_list.append(AMENITY_TYPE_LIST.index(amenity_type) + 1)
            else:
                amenity_salience_list.append(1)

    amenity_distance_list_max = max(amenity_distance_list, default=0)
    for i in range(len(amenity_distance_list)):
        weight = (W1 * (1 - (amenity_distance_list[i] / amenity_distance_list_max))) + (W2 * amenity_salience_list[i])
        amenity_value += weight

    return amenity_value


