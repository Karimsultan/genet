import argparse
import genet as gn
import logging
import time
import os
import json


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Create a road-only MATSim network')

    arg_parser.add_argument('-o',
                            '--osm',
                            help='Location of the osm file',
                            required=True)

    arg_parser.add_argument('-c',
                            '--config',
                            help='Location of the config file defining what and how to read from the osm file',
                            required=True)

    arg_parser.add_argument('-cc',
                            '--connected_components',
                            help='Number of connected components within graph for modes `walk`,`bike`,`car`',
                            default=1)

    arg_parser.add_argument('-p',
                            '--projection',
                            help='The projection for the network eg. "epsg:27700"',
                            required=True)

    arg_parser.add_argument('-pp',
                            '--processes',
                            help='Number of parallel processes to split process across',
                            default=1,
                            type=int)

    arg_parser.add_argument('-od',
                            '--output_dir',
                            help='Output directory for the network',
                            required=True)

    args = vars(arg_parser.parse_args())
    osm = args['osm']
    config = args['config']
    connected_components = args['connected_components']
    projection = args['projection']
    processes = args['processes']
    output_dir = args['output_dir']

    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.WARNING)

    n = gn.Network(projection)
    logging.info(f'Reading in OSM data at {osm}')
    start_network = time.time()
    n.read_osm(osm, config, num_processes=processes)
    logging.info(f'Extracting {connected_components} strongly connected components')
    for mode in ['walk', 'car', 'bike']:
        n.retain_n_connected_subgraphs(n=connected_components, mode=mode)

    n.write_to_matsim(os.path.join(output_dir, 'pre_simplify'))

    logging.info('Simplifying the Network.')
    start_simplify = time.time()
    n.simplify(no_processes=1)
    end_simplify = time.time()

    logging.info(
        f'Simplification resulted in {len(n.link_simplification_map)} links being simplified.')
    with open(os.path.join(output_dir, 'link_simp_map.json'), 'w', encoding='utf-8') as f:
        json.dump(n.link_simplification_map, f, ensure_ascii=False, indent=4)

    end_network = time.time()
    n.write_to_matsim(output_dir)

    logging.info('Generating validation report')
    report = n.generate_validation_report()
    logging.info(f'Graph validation: {report["graph"]["graph_connectivity"]}')

    n.generate_standard_outputs(os.path.join(output_dir, 'standard_outputs'))

    logging.info(f'It took {round((end_simplify - start_simplify)/60, 3)} min to simplify the network.')
    logging.info(f'It took {round((end_network - start_network)/60, 3)} min to generate the network.')

    n.write_to_matsim(output_dir)
