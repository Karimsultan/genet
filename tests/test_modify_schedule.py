import pytest
import sys
import os
from pyproj import Transformer
from pandas import DataFrame
from genet import Stop, Route, Service, Schedule, Network, MaxStableSet
from genet.modify import schedule as mod_schedule
import genet.utils.spatial as spatial
from tests.fixtures import assert_semantically_equal


def test_reproj_stops():
    stops = {'26997928P': {'routes': ['10314_0'], 'id': '26997928P', 'x': 528464.1342843144, 'y': 182179.7435136598,
                           'epsg': 'epsg:27700', 'lat': 51.52393050617373, 'lon': -0.14967658860132668,
                           's2_id': 5221390302759871369, 'additional_attributes': [], 'services': ['10314']},
             '26997928P.link:1': {'routes': ['10314_0'], 'id': '26997928P.link:1', 'x': 528464.1342843144,
                                  'y': 182179.7435136598, 'epsg': 'epsg:27700', 'lat': 51.52393050617373,
                                  'lon': -0.14967658860132668, 's2_id': 5221390302759871369,
                                  'additional_attributes': [], 'services': ['10314']}}
    reprojected = mod_schedule.reproj_stops(stops, 'epsg:4326')
    assert_semantically_equal(reprojected,
                              {'26997928P': {'x': -0.14967658860132668, 'y': 51.52393050617373, 'epsg': 'epsg:4326'},
                               '26997928P.link:1': {'x': -0.14967658860132668, 'y': 51.52393050617373,
                                                    'epsg': 'epsg:4326'}})


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
network_test_file = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "test_data", "simplified_network", "network.xml"))
schedule_test_file = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "test_data", "simplified_network", "schedule.xml"))


@pytest.fixture()
def test_network():
    n = Network('epsg:27700')
    n.read_matsim_network(network_test_file)
    n.read_matsim_schedule(schedule_test_file)
    return n


@pytest.fixture()
def test_spatialtree(test_network):
    return spatial.SpatialTree(test_network)


@pytest.fixture()
def test_service():
    return Service(
        id='service_bus',
        routes=[
            Route(id='route_1',
                  route_short_name='',
                  mode='bus',
                  stops=[Stop(epsg='epsg:27700', id='490004695A', x=529871.7641447927, y=181148.2259665833),
                         Stop(epsg='epsg:27700', id='490000235C', x=529741.7652299237, y=181516.3450505745),
                         Stop(epsg='epsg:27700', id='490000089A', x=529488.7339130711, y=181894.12649680028)],
                  trips={'trip_id': ['trip_1'],
                         'trip_departure_time': ['15:30:00'],
                         'vehicle_id': ['veh_bus_0']},
                  arrival_offsets=['00:00:00', '00:02:00', '00:05:00'],
                  departure_offsets=['00:00:00', '00:03:00', '00:07:00']
                  ),
            Route(id='route_2',
                  route_short_name='',
                  mode='bus',
                  stops=[Stop(epsg='epsg:27700', id='490000089A', x=529488.7339130711, y=181894.12649680028),
                         Stop(epsg='epsg:27700', id='490000252X', x=529299.7788544403, y=182221.2500579671),
                         Stop(epsg='epsg:27700', id='490000078Q', x=529350.7866918372, y=182388.01590025262)],
                  trips={'trip_id': ['trip_2'],
                         'trip_departure_time': ['16:30:00'],
                         'vehicle_id': ['veh_bus_1']},
                  arrival_offsets=['00:00:00', '00:02:00', '00:05:00'],
                  departure_offsets=['00:00:00', '00:03:00', '00:07:00']
                  )
        ])


def test_snapping_pt_route_results_in_all_stops_with_link_references_and_routes_between_them(
        test_network, test_spatialtree):
    mss = MaxStableSet(pt_graph=test_network.schedule.route('40230_1').graph(),
                       network_spatial_tree=test_spatialtree,
                       modes={'car', 'bus'},
                       distance_threshold=10,
                       step_size=10)

    mss.solve()
    assert mss.all_stops_solved()
    mss.route_edges()
    assert mss.pt_edges['shortest_path'].notna().all()


def test_snapping_partial_pt_route_results_in_all_stops_with_link_references_and_routes_between_viable_catchments(
        mocker, test_network, test_spatialtree):
    df = DataFrame({
        'index_left': {4: 4611, 5: 2836, 6: 1620, 7: 1619, 8: 4612, 9: 4611,
                       10: 1929, 11: 17, 12: 18, 13: 2291, 14: 17, 15: 2804, 16: 3361},
        'link_id': {4: '5221390698590575489_5221390721979501095', 5: '52213908340665748775221390828301496736',
                    6: '5221390721979501095_5221390721979501095', 7: '5221390721979501095_5221390721985855617',
                    8: '5221390698590575489_5221390698590575489', 9: '5221390698590575489_5221390721979501095',
                    10: '5221390698557344687_5221390698590575489', 11: '5221390688502743083_5221390698590575489',
                    12: '5221390688502743083_5221390688502743083', 13: '5221390319100521975_5221390688502743083',
                    14: '5221390688502743083_5221390698590575489', 15: '5221390319261602009_5221390688502743083',
                    16: '5221390688613602227_5221390688502743083'},
        'id': {4: '5221390721979501095', 5: '5221390721979501095', 6: '5221390721979501095', 7: '5221390721979501095',
               8: '5221390698590575489', 9: '5221390698590575489', 10: '5221390698590575489',
               11: '5221390698590575489', 12: '5221390688502743083', 13: '5221390688502743083',
               14: '5221390688502743083', 15: '5221390688502743083', 16: '5221390688502743083'},
        'catchment': {4: 5, 5: 5, 6: 5, 7: 5, 8: 5, 9: 5,
                      10: 5, 11: 5, 12: 5, 13: 5, 14: 5, 15: 5, 16: 5},
        'problem_nodes': {
            4: '5221390721979501095.link:5221390698590575489_5221390721979501095',
            5: '5221390721979501095.link:52213908340665748775221390828301496736',
            6: '5221390721979501095.link:5221390721979501095_5221390721979501095',
            7: '5221390721979501095.link:5221390721979501095_5221390721985855617',
            8: '5221390698590575489.link:5221390698590575489_5221390698590575489',
            9: '5221390698590575489.link:5221390698590575489_5221390721979501095',
            10: '5221390698590575489.link:5221390698557344687_5221390698590575489',
            11: '5221390698590575489.link:5221390688502743083_5221390698590575489',
            12: '5221390688502743083.link:5221390688502743083_5221390688502743083',
            13: '5221390688502743083.link:5221390319100521975_5221390688502743083',
            14: '5221390688502743083.link:5221390688502743083_5221390698590575489',
            15: '5221390688502743083.link:5221390319261602009_5221390688502743083',
            16: '5221390688502743083.link:5221390688613602227_5221390688502743083'}}).set_index('id', drop=False)
    df.index.rename(name='index', inplace=True)
    mocker.patch.object(spatial.SpatialTree, 'closest_links',
                        return_value=df)

    mss = MaxStableSet(pt_graph=test_network.schedule.route('40230_1').graph(),
                       network_spatial_tree=test_spatialtree,
                       modes={'car', 'bus'},
                       distance_threshold=5,
                       step_size=5)
    assert not mss.all_stops_have_nearest_links()
    mss.solve()
    assert mss.unsolved_stops == {'5221390319100521975'}
    mss.route_edges()
    assert set(mss.pt_edges[mss.pt_edges['shortest_path'].isna()]['u']) == {'5221390319100521975'}
    assert set(mss.pt_edges[mss.pt_edges['shortest_path'].isna()]['v']) == {'5221390688502743083'}


def test_snapping_disconnected_partial_pt_route_results_in_all_stops_with_link_references_and_routes_between_viable_catchments(
        mocker, test_network, test_spatialtree):
    df = DataFrame({
        'index_left': {0: 2291, 1: 2290, 2: 2292, 3: 5178, 4: 4611, 5: 2836, 6: 1620, 7: 1619, 8: 4612, 9: 4611,
                       10: 1929, 11: 17, 12: 18, 13: 2291, 14: 17, 15: 2804, 16: 3361},
        'link_id': {0: '5221390319100521975_5221390688502743083', 1: '5221390319100521975_5221390319062365867',
                    2: '5221390319100521975_5221390319100521975', 3: '5221390319091334983_5221390319100521975',
                    4: '5221390698590575489_5221390721979501095', 5: '52213908340665748775221390828301496736',
                    6: '5221390721979501095_5221390721979501095', 7: '5221390721979501095_5221390721985855617',
                    12: '5221390688502743083_5221390688502743083', 13: '5221390319100521975_5221390688502743083',
                    14: '5221390688502743083_5221390698590575489', 15: '5221390319261602009_5221390688502743083',
                    16: '5221390688613602227_5221390688502743083'},
        'id': {0: '5221390319100521975', 1: '5221390319100521975', 2: '5221390319100521975', 3: '5221390319100521975',
               4: '5221390721979501095', 5: '5221390721979501095', 6: '5221390721979501095', 7: '5221390721979501095',
               12: '5221390688502743083', 13: '5221390688502743083',
               14: '5221390688502743083', 15: '5221390688502743083', 16: '5221390688502743083'},
        'catchment': {0: 5, 1: 5, 2: 5, 3: 5, 4: 5, 5: 5, 6: 5, 7: 5, 12: 5, 13: 5, 14: 5, 15: 5, 16: 5},
        'problem_nodes': {
            0: '5221390319100521975.link:5221390319100521975_5221390688502743083',
            1: '5221390319100521975.link:5221390319100521975_5221390319062365867',
            2: '5221390319100521975.link:5221390319100521975_5221390319100521975',
            3: '5221390319100521975.link:5221390319091334983_5221390319100521975',
            4: '5221390721979501095.link:5221390698590575489_5221390721979501095',
            5: '5221390721979501095.link:52213908340665748775221390828301496736',
            6: '5221390721979501095.link:5221390721979501095_5221390721979501095',
            7: '5221390721979501095.link:5221390721979501095_5221390721985855617',
            12: '5221390688502743083.link:5221390688502743083_5221390688502743083',
            13: '5221390688502743083.link:5221390319100521975_5221390688502743083',
            14: '5221390688502743083.link:5221390688502743083_5221390698590575489',
            15: '5221390688502743083.link:5221390319261602009_5221390688502743083',
            16: '5221390688502743083.link:5221390688613602227_5221390688502743083'}}).set_index('id', drop=False)
    df.index.rename(name='index', inplace=True)
    mocker.patch.object(spatial.SpatialTree, 'closest_links',
                        return_value=df)

    mss = MaxStableSet(pt_graph=test_network.schedule.route('40230_1').graph(),
                       network_spatial_tree=test_spatialtree,
                       modes={'car', 'bus'},
                       distance_threshold=5,
                       step_size=5)
    assert not mss.all_stops_have_nearest_links()
    mss.solve()
    assert mss.unsolved_stops == {'5221390698590575489', '5221390721979501095'}
    mss.route_edges()
    assert set(mss.pt_edges[mss.pt_edges['shortest_path'].isna()]['u']) == {'5221390698590575489',
                                                                            '5221390688502743083'}
    assert set(mss.pt_edges[mss.pt_edges['shortest_path'].isna()]['v']) == {'5221390698590575489',
                                                                            '5221390721979501095'}


def test_artificially_filling_in_solution_for_partial_pt_routing_problem_results_in_correct_solution_and_routed_path(
        mocker, test_network, test_spatialtree):
    df = DataFrame({
        'index_left': {4: 4611, 5: 2836, 6: 1620, 7: 1619, 8: 4612, 9: 4611,
                       10: 1929, 11: 17, 12: 18, 13: 2291, 14: 17, 15: 2804, 16: 3361},
        'link_id': {4: '5221390698590575489_5221390721979501095', 5: '52213908340665748775221390828301496736',
                    6: '5221390721979501095_5221390721979501095', 7: '5221390721979501095_5221390721985855617',
                    8: '5221390698590575489_5221390698590575489', 9: '5221390698590575489_5221390721979501095',
                    10: '5221390698557344687_5221390698590575489', 11: '5221390688502743083_5221390698590575489',
                    12: '5221390688502743083_5221390688502743083', 13: '5221390319100521975_5221390688502743083',
                    14: '5221390688502743083_5221390698590575489', 15: '5221390319261602009_5221390688502743083',
                    16: '5221390688613602227_5221390688502743083'},
        'id': {4: '5221390721979501095', 5: '5221390721979501095', 6: '5221390721979501095', 7: '5221390721979501095',
               8: '5221390698590575489', 9: '5221390698590575489', 10: '5221390698590575489',
               11: '5221390698590575489', 12: '5221390688502743083', 13: '5221390688502743083',
               14: '5221390688502743083', 15: '5221390688502743083', 16: '5221390688502743083'},
        'catchment': {4: 5, 5: 5, 6: 5, 7: 5, 8: 5, 9: 5,
                      10: 5, 11: 5, 12: 5, 13: 5, 14: 5, 15: 5, 16: 5},
        'problem_nodes': {
            4: '5221390721979501095.link:5221390698590575489_5221390721979501095',
            5: '5221390721979501095.link:52213908340665748775221390828301496736',
            6: '5221390721979501095.link:5221390721979501095_5221390721979501095',
            7: '5221390721979501095.link:5221390721979501095_5221390721985855617',
            8: '5221390698590575489.link:5221390698590575489_5221390698590575489',
            9: '5221390698590575489.link:5221390698590575489_5221390721979501095',
            10: '5221390698590575489.link:5221390698557344687_5221390698590575489',
            11: '5221390698590575489.link:5221390688502743083_5221390698590575489',
            12: '5221390688502743083.link:5221390688502743083_5221390688502743083',
            13: '5221390688502743083.link:5221390319100521975_5221390688502743083',
            14: '5221390688502743083.link:5221390688502743083_5221390698590575489',
            15: '5221390688502743083.link:5221390319261602009_5221390688502743083',
            16: '5221390688502743083.link:5221390688613602227_5221390688502743083'}}).set_index('id', drop=False)
    df.index.rename(name='index', inplace=True)
    mocker.patch.object(spatial.SpatialTree, 'closest_links',
                        return_value=df)

    mss = MaxStableSet(pt_graph=test_network.schedule.route('40230_1').graph(),
                       network_spatial_tree=test_spatialtree,
                       modes={'car', 'bus'},
                       distance_threshold=5,
                       step_size=5)
    assert not mss.all_stops_have_nearest_links()
    mss.solve()
    assert mss.unsolved_stops == {'5221390319100521975'}
    mss.route_edges()
    mss.fill_in_solution_artificially()

    art_link = 'artificial_link===from:5221390319100521975===to:5221390319100521975'
    assert mss.solution['5221390319100521975'] == art_link
    art_stop = '5221390319100521975.link:artificial_link===from:5221390319100521975===to:5221390319100521975'
    assert art_stop in mss.artificial_stops
    assert mss.artificial_stops[art_stop]['linkRefId'] == art_link
    assert mss.artificial_stops[art_stop]['stop_id'] == '5221390319100521975'
    assert mss.artificial_stops[art_stop]['id'] == art_stop
    assert mss.routed_path(
        ['5221390319100521975', '5221390688502743083', '5221390698590575489', '5221390721979501095']) == [
               'artificial_link===from:5221390319100521975===to:5221390319100521975',
               'artificial_link===from:5221390319100521975===to:5221390688502743083',
               '5221390688502743083_5221390698590575489', '5221390698590575489_5221390721979501095']


def test_routing_service_with_network(test_network, test_service):
    test_network.schedule = Schedule(epsg='epsg:27700', services=[test_service])
    test_network.route_service('service_bus')

    rep = test_network.generate_validation_report()
    assert rep['graph']['graph_connectivity']['car']['number_of_connected_subgraphs'] == 1
    assert rep['schedule']['schedule_level']['is_valid_schedule']
    assert rep['routing']['services_have_routes_in_the_graph']
