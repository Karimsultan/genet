import json
import os
import sys
from collections import OrderedDict

import dictdiffer
from pyproj import Proj, Transformer

from genet.inputs_handler import matsim_reader

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
pt2matsim_network_test_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data", "network.xml"))
pt2matsim_network_multiple_edges_test_file = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "test_data", "network_multiple_edges.xml"))
pt2matsim_schedule_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data", "schedule.xml"))


def test_read_network_builds_graph_with_correct_data_on_nodes_and_edges():
    correct_nodes = {
        '21667818': {'id': '21667818', 's2_id': 5221390302696205321, 'x': '528504.1342843144', 'y': '182155.7435136598',
                     'lon': -0.14910908709500162, 'lat': 51.52370573323939},
        '25508485': {'id': '25508485', 's2_id': 5221390301001263407, 'x': '528489.467895946', 'y': '182206.20303669578',
                     'lon': -0.14930198709481451, 'lat': 51.524162533239284}}

    correct_edges = {'25508485_21667818': {
        'id': "1", 'from': "25508485", 'to': "21667818", 'length': 52.765151087870265,
        's2_from': 5221390301001263407, 's2_to': 5221390302696205321,
        'freespeed': "4.166666666666667", 'capacity': "600.0", 'permlanes': "1.0", 'oneway': "1",
        'modes': ['subway,metro', 'walk', 'car'], 'attributes': {
            'osm:way:access': {'name': 'osm:way:access', 'class': 'java.lang.String', 'text': 'permissive'},
            'osm:way:highway': {'name': 'osm:way:highway', 'class': 'java.lang.String', 'text': 'unclassified'},
            'osm:way:id': {'name': 'osm:way:id', 'class': 'java.lang.Long', 'text': '26997928'},
            'osm:way:name': {'name': 'osm:way:name', 'class': 'java.lang.String', 'text': 'Brunswick Place'}
        }}}

    transformer = Transformer.from_proj(Proj(init='epsg:27700'), Proj(init='epsg:4326'))

    g, node_id_mapping, link_id_mapping = matsim_reader.read_network(pt2matsim_network_test_file, transformer)

    for u, data in g.nodes(data=True):
        assert str(u) in correct_nodes
        assert_semantically_equal(data, correct_nodes[str(u)])

    for u, v, data in g.edges(data=True):
        edge = '{}_{}'.format(u, v)
        assert edge in correct_edges
        assert_semantically_equal(data, correct_edges[edge])


def test_read_network_builds_graph_with_multiple_edges_with_correct_data_on_nodes_and_edges():
    correct_nodes = {
        '21667818': {'id': '21667818', 's2_id': 5221390302696205321, 'x': '528504.1342843144', 'y': '182155.7435136598',
                     'lon': -0.14910908709500162, 'lat': 51.52370573323939},
        '25508485': {'id': '25508485', 's2_id': 5221390301001263407, 'x': '528489.467895946', 'y': '182206.20303669578',
                     'lon': -0.14930198709481451, 'lat': 51.524162533239284}}

    correct_edges = {'25508485_21667818': {
        0: {
            'id': "1", 'from': "25508485", 'to': "21667818", 'length': 52.765151087870265,
            's2_from': 5221390301001263407, 's2_to': 5221390302696205321,
            'freespeed': "4.166666666666667", 'capacity': "600.0", 'permlanes': "1.0", 'oneway': "1",
            'modes': ['walk', 'car'], 'attributes': {
                'osm:way:access': {'name': 'osm:way:access', 'class': 'java.lang.String', 'text': 'permissive'},
                'osm:way:highway': {'name': 'osm:way:highway', 'class': 'java.lang.String', 'text': 'unclassified'},
                'osm:way:id': {'name': 'osm:way:id', 'class': 'java.lang.Long', 'text': '26997928'},
                'osm:way:name': {'name': 'osm:way:name', 'class': 'java.lang.String', 'text': 'Brunswick Place'}}
        },
        1: {
            'id': "2", 'from': "25508485", 'to': "21667818", 'length': 52.765151087870265,
            's2_from': 5221390301001263407, 's2_to': 5221390302696205321,
            'freespeed': "4.166666666666667", 'capacity': "600.0", 'permlanes': "1.0", 'oneway': "1",
            'modes': ['bus'], 'attributes': {
                'osm:way:lanes': {'name': 'osm:way:lanes', 'class': 'java.lang.String', 'text': '1'},
                'osm:way:highway': {'name': 'osm:way:highway', 'class': 'java.lang.String', 'text': 'unclassified'},
                'osm:way:id': {'name': 'osm:way:id', 'class': 'java.lang.Long', 'text': '26997928'},
                'osm:way:name': {'name': 'osm:way:name', 'class': 'java.lang.String', 'text': 'Brunswick Place'},
                'osm:way:oneway': {'name': 'osm:way:oneway', 'class': 'java.lang.String', 'text': 'yes'},
                'osm:relation:route': {'class': 'java.lang.String', 'name': 'osm:relation:route', 'text': 'bus,bicycle'}
            }
        }}}

    transformer = Transformer.from_proj(Proj(init='epsg:27700'), Proj(init='epsg:4326'))

    g, node_id_mapping, link_id_mapping = matsim_reader.read_network(pt2matsim_network_multiple_edges_test_file,
                                                                     transformer)

    for u, data in g.nodes(data=True):
        assert str(u) in correct_nodes
        assert_semantically_equal(data, correct_nodes[str(u)])

    for edge in g.edges:
        e = '{}_{}'.format(edge[0], edge[1])
        assert e in correct_edges
        assert edge[2] in correct_edges[e]
        assert_semantically_equal(g[edge[0]][edge[1]][edge[2]], correct_edges[e][edge[2]])


def test_read_schedule_reads_the_data_correctly():
    correct_schedule = {'10314': [{
        'route_short_name': '12',
        'mode': 'bus',
        'stops': ['26997928P', '26997928P.link:1'],
        's2_stops': [5221390302759871369, 5221390302759871369],
        'route': ['1'],
        'trips': {'VJ00938baa194cee94700312812d208fe79f3297ee_04:40:00': '04:40:00'},
        'arrival_offsets': ['00:00:00', '00:02:00'],
        'departure_offsets': ['00:00:00', '00:02:00']}]}

    transformer = Transformer.from_proj(Proj(init='epsg:27700'), Proj(init='epsg:4326'))

    schedule, transit_stop_id_mapping = matsim_reader.read_schedule(pt2matsim_schedule_file, transformer)

    assert_semantically_equal(schedule, correct_schedule)


###########################################################
# helper functions
###########################################################
def deep_sort(obj):
    if isinstance(obj, dict):
        obj = OrderedDict(sorted(obj.items()))
        for k, v in obj.items():
            if isinstance(v, dict) or isinstance(v, list):
                obj[k] = deep_sort(v)

    if isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, dict) or isinstance(v, list):
                obj[i] = deep_sort(v)
        obj = sorted(obj, key=lambda x: json.dumps(x))

    return obj


def assert_semantically_equal(dict1, dict2):
    # the tiny permissible tolerance is to account for cross-platform differences in
    # floating point lat/lon values, as witnessed in our CI build running on Ubuntu
    # Vs our own OSX laptops - lat/lon values within this tolerance can and should
    # be considered the same in practical terms
    assert list(dictdiffer.diff(deep_sort(dict1), deep_sort(dict2), tolerance=0.000000000000001)) == []
