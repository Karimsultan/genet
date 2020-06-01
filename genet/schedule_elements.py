from typing import Union, Dict, List
from pyproj import Proj, Transformer
from genet.utils import spatial

# number of decimal places to consider when comparing lat lons
SPATIAL_TOLERANCE = 8


class Stop:
    """
    A transit stop that features in a Route object

    Parameters
    ----------
    :param id: unique identifier
    :param x: x coordinate or lon if using 'epsg:4326'
    :param y: y coordinate or lat if using 'epsg:4326'
    :param epsg: 'epsg:12345'
    :param transformer: optional but makes things MUCH faster if you're reading through a lot of stops in the same
            projection
    """

    def __init__(self, id: Union[str, int], x: Union[str, int, float], y: Union[str, int, float], epsg: str,
                 transformer: Transformer = None):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.epsg = epsg
        if transformer is None:
            self.transformer = Transformer.from_proj(Proj(init=epsg), Proj(init='epsg:4326'))
        else:
            self.transformer = transformer

        if self.epsg == 'epsg:4326':
            self.lon, self.lat = float(x), float(y)
        else:
            self.lon, self.lat = spatial.change_proj(x, y, self.transformer)

    def __eq__(self, other):
        return (round(self.lat, SPATIAL_TOLERANCE) == round(other.lat, SPATIAL_TOLERANCE)) \
               and (round(self.lon, SPATIAL_TOLERANCE) == round(other.lon, SPATIAL_TOLERANCE))

    def __hash__(self):
        return hash((self.id, round(self.lat, SPATIAL_TOLERANCE), round(self.lon, SPATIAL_TOLERANCE)))

    def add_additional_attributes(self, attribs: dict):
        """
        adds attributes defined by keys of the attribs dictionary with values of the corresponding values
        ignores keys: 'id', 'x', 'y'
        :param attribs:
        :return:
        """
        for k, v in attribs.items():
            if k not in ['id', 'x', 'y']:
                setattr(self, k, v)

    def is_exact(self, other):
        same_id = self.id == other.id
        same_lat = (round(self.lat, SPATIAL_TOLERANCE) == round(other.lat, SPATIAL_TOLERANCE))
        same_lon = (round(self.lon, SPATIAL_TOLERANCE) == round(other.lon, SPATIAL_TOLERANCE))
        return same_id and same_lat and same_lon

    def isin_exact(self, stops: list):
        for other in stops:
            if self.is_exact(other):
                return True
        return False


class Route:
    """
    A Route is an object which contains information about the trips, times and offsets, mode and name of the route which
    forms a part of a Service.

    Parameters
    ----------
    :param route_short_name: route's short name
    :param mode: mode
    :param stops: list of Stop class objects
    :param trips: dictionary {'trip_id' : 'HH:MM:SS' - departure time from first stop}
    :param arrival_offsets: list of 'HH:MM:SS' temporal offsets for each of the stops_mapping
    :param departure_offsets: list of 'HH:MM:SS' temporal offsets for each of the stops_mapping
    :param route: optional, network link_ids traversed by the vehicles in this Route instance
    """

    def __init__(self, route_short_name: str, mode: str, stops: List[Stop], trips: Dict[str, str],
                 arrival_offsets: List[str], departure_offsets: List[str], route: list = None):
        self.route_short_name = route_short_name
        self.mode = mode
        self.stops = stops
        self.trips = trips
        self.arrival_offsets = arrival_offsets
        self.departure_offsets = departure_offsets

        if route is None:
            self.route = []
        else:
            self.route = route

    def __eq__(self, other):
        same_route_name = self.route_short_name == other.route_short_name
        same_mode = self.mode.lower() == other.mode.lower()
        same_stops = self.stops == other.stops
        return same_route_name and same_mode and same_stops

    def is_exact(self, other):
        same_route_name = self.route_short_name == other.route_short_name
        same_mode = self.mode.lower() == other.mode.lower()
        same_stops = self.stops == other.stops
        same_trips = self.trips == other.trips
        same_arrival_offsets = self.arrival_offsets == other.arrival_offsets
        same_departure_offsets = self.departure_offsets == other.departure_offsets

        statement = same_route_name and same_mode and same_stops and same_trips and same_arrival_offsets \
            and same_departure_offsets
        return statement

    def isin_exact(self, routes: list):
        for other in routes:
            if self.is_exact(other):
                return True
        return False


class Service:
    """
    A Service is an object containing unique routes pertaining to the same public transit service

    Parameters
    ----------
    :param services: dictionary of Service class objects {'service_id' : Service}
    :param stops_mapping: dictionary of Stop class objects {'stop_id': Stop} which pertain to the Services
    :param epsg: 'epsg:12345'
    """

    def __init__(self, id: str, routes: List[Route]):
        self.id = id
        self.routes = routes

    def __eq__(self, other):
        return self.id == other.id

    def is_exact(self, other):
        return (self.id == other.id) and (self.routes == other.routes)

    def isin_exact(self, services: list):
        for other in services:
            if self.is_exact(other):
                return True
        return False

    def stops(self):
        """
        Iterable returns unique stops for all routes within the service
        :return:
        """
        all_stops = set()
        for route in self.routes:
            all_stops = all_stops | set(route.stops)
        for stop in all_stops:
            yield stop
