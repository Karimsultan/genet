import logging
from math import ceil
from statistics import median

from shapely.geometry import LineString, Point

import genet.utils.parallel as parallel


# rip and monkey patch of a few functions from osmnx.simplification to customise graph simplification


def _process_path(indexed_edge_groups_to_simplify):
    links_to_add = {}
    for new_id, edge_group_data in indexed_edge_groups_to_simplify.items():
        path = edge_group_data['path']
        nodes_data = edge_group_data['node_data']
        edge_attributes = edge_group_data['link_data'].copy()

        if 'attributes' in edge_attributes:
            new_attributes = {}
            for attribs_dict in edge_attributes['attributes']:
                for key, val in attribs_dict.items():
                    if key in new_attributes:
                        new_attributes[key]['text'] |= {val["text"]}
                    else:
                        new_attributes[key] = val.copy()
                        new_attributes[key]['text'] = {new_attributes[key]['text']}
            for key, val in new_attributes.items():
                if len(val['text']) == 1:
                    val['text'] = list(val['text'])[0]
            edge_attributes['attributes'] = new_attributes.copy()

        # construct the geometry
        edge_attributes["geometry"] = LineString(
            [Point((nodes_data[node]["x"], nodes_data[node]["y"])) for node in path]
        )

        edge_attributes['ids'] = edge_attributes['id']
        edge_attributes['id'] = new_id

        edge_attributes['from'] = path[0]
        edge_attributes['to'] = path[-1]
        edge_attributes['s2_from'] = nodes_data[path[0]]['s2_id']
        edge_attributes['s2_to'] = nodes_data[path[-1]]['s2_id']

        edge_attributes['freespeed'] = max(edge_attributes['freespeed'])
        edge_attributes['capacity'] = ceil(median(edge_attributes['capacity']))
        edge_attributes['permlanes'] = ceil(median(edge_attributes['permlanes']))
        edge_attributes['length'] = sum(edge_attributes['length'])

        modes = set()
        for mode_list in edge_attributes['modes']:
            modes |= set(mode_list)
        edge_attributes['modes'] = modes

        for key in set(edge_attributes) - {'s2_to', 'freespeed', 'attributes', 'to', 'permlanes', 'from', 'id', 'ids',
                                           'capacity', 'length', 'modes', 's2_from', 'geometry'}:
            if len(set(edge_attributes[key])) == 1:
                # if there's only 1 unique value in this attribute list,
                # consolidate it to the single value (the zero-th)
                edge_attributes[key] = edge_attributes[key][0]
            else:
                # otherwise, if there are multiple values, keep one of each value
                edge_attributes[key] = list(set(edge_attributes[key]))

        links_to_add[new_id] = edge_attributes
    return links_to_add


def _extract_edge_data(n, path):
    edge_attributes = {}
    for u, v in zip(path[:-1], path[1:]):
        # get edge between these nodes: if multiple edges exist between
        # them - smoosh them
        for multi_idx, edge in n.graph[u][v].items():
            for key in edge:
                if key in edge_attributes:
                    # if this key already exists in the dict, append it to the
                    # value list
                    edge_attributes[key].append(edge[key])
                else:
                    # if this key doesn't already exist, set the value to a list
                    # containing the one value
                    edge_attributes[key] = [edge[key]]
    n.remove_links(edge_attributes['id'], ignore_change_log=True, silent=True)
    return edge_attributes


def _extract_node_data(n, path):
    return {node: n.node(node) for node in path}


def _assemble_path_data(n, indexed_paths_to_simplify):
    return_d = {}
    for k, path in indexed_paths_to_simplify.items():
        return_d[k] = {
            'path': path,
            'link_data': _extract_edge_data(n, path),
            'node_data': _extract_node_data(n, path),
            'nodes_to_remove': path[1:-1]
        }
        return_d[k]['ids'] = set(return_d[k]['link_data']['id'])
    return return_d


def _is_endpoint(node_neighbours):
    """
    :param node_neighbours: dict {node: {
     successors: {set of nodes that you can reach from node},
     predecessors: {set of nodes that lead to node}
    }}
    :return:
    """
    return [node for node, data in node_neighbours.items() if
            ((len(data['successors'] | data['predecessors']) > 2) or
             (not data['successors'] or not data['predecessors']) or
             (node in data['successors']) or
             (len(data['successors']) != len(data['predecessors'])) or
             ((len(data['successors'] | data['predecessors']) == 1) and (data['successors'] == data['predecessors'])))]


def _build_paths(path_start_points, endpoints, neighbours):
    paths = []
    logging.info(f"Processing {len(path_start_points)} paths")
    for path_start_point in path_start_points:
        if path_start_point[1] not in endpoints:
            path = list(path_start_point)
            end_node = path[-1]
            while end_node not in endpoints:
                if neighbours[end_node] == {path[0]}:
                    end_node = path[0]
                elif len(neighbours[end_node]) > 1:
                    next_nodes = neighbours[end_node] - {path[-2]}
                    if len(next_nodes) > 1:
                        raise RuntimeError('Path building found additional branching. Simplification failed to find'
                                           'all of the correct end points.')
                    end_node = list(next_nodes)[0]
                else:
                    end_node = list(neighbours[end_node])[0]
                path.append(end_node)
            paths.append(path)
    return paths


def _get_edge_groups_to_simplify(G, no_processes=1):
    # first identify all the nodes that are endpoints
    endpoints = set(
        parallel.multiprocess_wrap(
            data={node: {'successors': set(G.successors(node)), 'predecessors': set(G.predecessors(node))}
                  for node in G.nodes},
            split=parallel.split_dict,
            apply=_is_endpoint,
            combine=parallel.combine_list,
            processes=no_processes)
    )

    logging.info(f"Identified {len(endpoints)} edge endpoints")
    path_start_points = list(G.out_edges(endpoints))

    logging.info(f"Identified {len(path_start_points)} possible paths")
    return parallel.multiprocess_wrap(
        data=path_start_points,
        split=parallel.split_list,
        apply=_build_paths,
        combine=parallel.combine_list,
        processes=no_processes,
        endpoints=endpoints,
        neighbours={node: set(G.neighbors(node)) for node in G.nodes}
    )


def simplify_graph(n, no_processes=1, suggested_map=None):
    """
    MONKEY PATCH OF OSMNX'S GRAPH SIMPLIFICATION ALGO

    Simplify a graph's topology by removing interstitial nodes.

    Simplify graph topology by removing all nodes that are not intersections
    or dead-ends. Create an edge directly between the end points that
    encapsulate them, but retain the geometry of the original edges, saved as
    attribute in new edge.

    Parameters
    ----------
    n: genet.Network object
    no_processes: number of processes to split some of the processess across
    suggested_map: dictionary of suggested link IDs mapping between old network and new links, does not affect
        how the graph gets simplified.

    Returns
    -------
    None, updates n.graph, indexing and schedule routes. Adds a new attribute to n that records map between old
    and new link indices
    """
    if suggested_map is None:
        suggested_map = {}

    logging.info("Begin simplifying the graph")
    initial_node_count = len(list(n.graph.nodes()))
    initial_edge_count = len(list(n.graph.edges()))

    logging.info('Generating paths to be simplified')
    # generate each path that needs to be simplified
    edges_to_simplify = [list(x) for x in
                         set(tuple(x) for x in _get_edge_groups_to_simplify(n.graph, no_processes=no_processes))]
    logging.info(f'Found {len(edges_to_simplify)} paths to simplify.')

    indexed_paths_to_simplify = dict(
        zip(n.generate_indices_for_n_edges(len(edges_to_simplify), avoid_keys=set(suggested_map.values())),
            edges_to_simplify))
    indexed_paths_to_simplify = _assemble_path_data(n, indexed_paths_to_simplify)

    failed_suggestions = set()
    if suggested_map:
        indexed_paths_to_simplify = reindex_paths(indexed_paths_to_simplify, suggested_map)
        failed_suggestions = set(suggested_map.values()) - set(indexed_paths_to_simplify)
        logging.info('Simplification with suggested mapping resulted in '
                     f'{len(set(suggested_map.values()) - failed_suggestions)}/{set(suggested_map.values())} IDs '
                     'being inherited from the suggested map')
        if failed_suggestions:
            logging.warning(f'{len(failed_suggestions)} suggested mappings failed.')

    nodes_to_remove = set()
    for k, data in indexed_paths_to_simplify.items():
        nodes_to_remove |= set(data['nodes_to_remove'])
    n.remove_nodes(nodes_to_remove, ignore_change_log=True, silent=True)

    logging.info('Processing links for all paths to be simplified')
    links_to_add = parallel.multiprocess_wrap(
        data=indexed_paths_to_simplify,
        split=parallel.split_dict,
        apply=_process_path,
        combine=parallel.combine_dict,
        processes=no_processes
    )

    logging.info('Adding new simplified links')
    # add links
    reindexing_dict = n.add_links(links_to_add, ignore_change_log=True)[0]

    # generate link simplification map between old indices and new, add changelog event
    for old_id, new_id in reindexing_dict.items():
        indexed_paths_to_simplify[new_id] = indexed_paths_to_simplify[old_id]
        del indexed_paths_to_simplify[old_id]
    new_ids = list(indexed_paths_to_simplify.keys())
    old_ids = [indexed_paths_to_simplify[_id]['ids'] for _id in new_ids]
    n.change_log = n.change_log.simplify_bunch(old_ids, new_ids, indexed_paths_to_simplify, links_to_add)
    del links_to_add

    # generate map between old and new ids
    n.link_simplification_map = {}
    for old_id_list, new_id in zip(old_ids, new_ids):
        for _id in old_id_list:
            n.link_simplification_map[_id] = new_id
    n.update_link_auxiliary_files(n.link_simplification_map)

    logging.info(
        f"Simplified graph: {initial_node_count} to {len(n.graph)} nodes, {initial_edge_count} to "
        f"{len(n.graph.edges())} edges")

    if n.schedule:
        logging.info("Updating the Schedule")
        # update stop's link reference ids
        n.schedule.apply_function_to_stops(n.link_simplification_map, 'linkRefId')
        logging.info("Updated Stop Link Reference Ids")

        # update schedule routes
        df_routes = n.schedule.route_attribute_data(keys=['route'])
        df_routes['route'] = df_routes['route'].apply(lambda x: update_link_ids(x, n.link_simplification_map))
        n.schedule.apply_attributes_to_routes(df_routes.T.to_dict())
        logging.info("Updated Network Routes")
        logging.info("Finished simplifying network")

    return failed_suggestions


def reindex_paths(indexed_paths_to_simplify, suggested_map):
    # initial link_id : simplified link ID map
    initial_indexed_map = {}
    for key, value in indexed_paths_to_simplify.items():
        initial_indexed_map = {**initial_indexed_map, **{_id: key for _id in value['ids']}}

    # create a map between initial and suggested IDs
    bridge_map = {initial_id: suggested_map[link_id] for link_id, initial_id in initial_indexed_map.items() if
                  link_id in suggested_map}

    # group by initial index
    grouped_bridge_map = {}
    for key, value in sorted(bridge_map.items()):
        grouped_bridge_map.setdefault(value, set()).add(key)

    # group the suggested map to reference later when checking for the same level of simplification
    grouped_suggested_map = {}
    for key, value in sorted(suggested_map.items()):
        grouped_suggested_map.setdefault(value, set()).add(key)

    # reindex those for which groups of links to be simplified coincide
    for inherited_idx, v in grouped_bridge_map.items():
        if len(v) == 1:
            initial_idx = list(v)[0]
            # check for coinciding level of simplification
            if grouped_suggested_map[inherited_idx] == indexed_paths_to_simplify[initial_idx]['ids']:
                # reindex
                indexed_paths_to_simplify[inherited_idx] = indexed_paths_to_simplify[initial_idx]
                del indexed_paths_to_simplify[initial_idx]

    return indexed_paths_to_simplify


def update_link_ids(old_route, link_mapping):
    new_route = []
    for link in old_route:
        updated_route_link = link
        try:
            updated_route_link = link_mapping[link]
        except KeyError:
            pass
        if not new_route:
            new_route = [updated_route_link]
        elif new_route[-1] != updated_route_link:
            new_route.append(updated_route_link)
    return new_route
