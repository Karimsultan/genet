import json
import dictdiffer
from collections import OrderedDict


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


###########################################################
# correct gtfs vars
###########################################################
correct_stop_times = [{'trip_id': 'BT1', 'arrival_time': '03:21:00', 'departure_time': '03:21:00', 'stop_id': 'BSE',
                       'stop_sequence': '0', 'stop_headsign': '', 'pickup_type': '0', 'drop_off_type': '1',
                       'timepoint': '1', 'stop_direction_name': ''},
                      {'trip_id': 'BT1', 'arrival_time': '03:23:00', 'departure_time': '03:23:00', 'stop_id': 'BSN',
                       'stop_sequence': '1', 'stop_headsign': '', 'pickup_type': '0', 'drop_off_type': '0',
                       'timepoint': '0', 'stop_direction_name': ''},
                      {'trip_id': 'RT1', 'arrival_time': '03:21:00', 'departure_time': '03:21:00', 'stop_id': 'RSN',
                       'stop_sequence': '0', 'stop_headsign': '', 'pickup_type': '0', 'drop_off_type': '0',
                       'timepoint': '0', 'stop_direction_name': ''},
                      {'trip_id': 'RT1', 'arrival_time': '03:23:00', 'departure_time': '03:23:00', 'stop_id': 'RSE',
                       'stop_sequence': '1', 'stop_headsign': '', 'pickup_type': '0', 'drop_off_type': '1',
                       'timepoint': '1', 'stop_direction_name': ''}]
correct_stop_times_db = {'BT1': [
    {'trip_id': 'BT1', 'arrival_time': '03:21:00', 'departure_time': '03:21:00', 'stop_id': 'BSE',
     'stop_sequence': '0', 'stop_headsign': '', 'pickup_type': '0', 'drop_off_type': '1', 'timepoint': '1',
     'stop_direction_name': ''},
    {'trip_id': 'BT1', 'arrival_time': '03:23:00', 'departure_time': '03:23:00', 'stop_id': 'BSN',
     'stop_sequence': '1', 'stop_headsign': '', 'pickup_type': '0', 'drop_off_type': '0', 'timepoint': '0',
     'stop_direction_name': ''}], 'RT1': [
    {'trip_id': 'RT1', 'arrival_time': '03:21:00', 'departure_time': '03:21:00', 'stop_id': 'RSN',
     'stop_sequence': '0', 'stop_headsign': '', 'pickup_type': '0', 'drop_off_type': '0', 'timepoint': '0',
     'stop_direction_name': ''},
    {'trip_id': 'RT1', 'arrival_time': '03:23:00', 'departure_time': '03:23:00', 'stop_id': 'RSE',
     'stop_sequence': '1', 'stop_headsign': '', 'pickup_type': '0', 'drop_off_type': '1', 'timepoint': '1',
     'stop_direction_name': ''}]}
correct_stops_db = {
    'BSE': {'stop_id': 'BSE', 'stop_code': '', 'stop_name': 'Bus Stop snap to edge', 'stop_lat': '51.5226864',
            'stop_lon': '-0.1413621', 'wheelchair_boarding': '', 'stop_timezone': '', 'location_type': '0.0',
            'parent_station': '210G433', 'platform_code': ''},
    'BSN': {'stop_id': 'BSN', 'stop_code': '', 'stop_name': 'Bus Stop snap to node', 'stop_lat': '51.5216199',
            'stop_lon': '-0.140053', 'wheelchair_boarding': '', 'stop_timezone': '', 'location_type': '0.0',
            'parent_station': '210G432', 'platform_code': ''},
    'RSE': {'stop_id': 'RSE', 'stop_code': '', 'stop_name': 'Rail Stop snap to edge', 'stop_lat': '51.5192615',
            'stop_lon': '-0.1421595', 'wheelchair_boarding': '', 'stop_timezone': '', 'location_type': '0.0',
            'parent_station': '210G431', 'platform_code': ''},
    'RSN': {'stop_id': 'RSN', 'stop_code': '', 'stop_name': 'Rail Stop snap to node', 'stop_lat': '51.5231335',
            'stop_lon': '-0.1410946', 'wheelchair_boarding': '', 'stop_timezone': '', 'location_type': '0.0',
            'parent_station': '210G430', 'platform_code': ''}}
correct_trips_db = {
    'BT1': {'route_id': '1001', 'service_id': '6630', 'trip_id': 'BT1', 'trip_headsign': 'Bus Test trip',
            'block_id': '', 'wheelchair_accessible': '0', 'trip_direction_name': '', 'exceptional': ''},
    'RT1': {'route_id': '1002', 'service_id': '6631', 'trip_id': 'RT1', 'trip_headsign': 'Rail Test trip',
            'block_id': '', 'wheelchair_accessible': '0', 'trip_direction_name': '', 'exceptional': ''}}
correct_routes_db = {'1001': {'route_id': '1001', 'agency_id': 'OP550', 'route_short_name': 'BTR',
                              'route_long_name': 'Bus Test Route', 'route_type': '3', 'route_url': '',
                              'route_color': 'CE312D', 'route_text_color': 'FFFFFF', 'checkin_duration': ''},
                     '1002': {'route_id': '1002', 'agency_id': 'OP550', 'route_short_name': 'RTR',
                              'route_long_name': 'Rail Test Route', 'route_type': '2', 'route_url': '',
                              'route_color': 'CE312D', 'route_text_color': 'FFFFFF', 'checkin_duration': ''}}

correct_schedule = {'1001': [
    {'route_short_name': 'BTR', 'route_long_name': 'Bus Test Route', 'mode': 'bus', 'route_color': '#CE312D',
     'trips': {'BT1': '03:21:00'}, 'stops': ['BSE', 'BSN'], 'arrival_offsets': ['0:00:00', '0:02:00'],
     'departure_offsets': ['0:00:00', '0:02:00'], 's2_stops': [5221390325135889957, 5221390684150342605]}], '1002': [
    {'route_short_name': 'RTR', 'route_long_name': 'Rail Test Route', 'mode': 'rail', 'route_color': '#CE312D',
     'trips': {'RT1': '03:21:00'}, 'stops': ['RSN', 'RSE'], 'arrival_offsets': ['0:00:00', '0:02:00'],
     'departure_offsets': ['0:00:00', '0:02:00'], 's2_stops': [5221390332291192399, 5221390324026756531]}]}

correct_stops = {'BSE': {'x': '-0.1413621', 'y': '51.5226864', 's2_node_id': 5221390325135889957},
                 'BSN': {'x': '-0.140053', 'y': '51.5216199', 's2_node_id': 5221390684150342605},
                 'RSE': {'x': '-0.1421595', 'y': '51.5192615', 's2_node_id': 5221390324026756531},
                 'RSN': {'x': '-0.1410946', 'y': '51.5231335', 's2_node_id': 5221390332291192399}}
