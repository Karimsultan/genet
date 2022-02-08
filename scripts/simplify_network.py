import argparse
import json
import logging
import os
import time

from genet import read_matsim
from genet.utils.persistence import ensure_dir

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Simplify a MATSim network by removing '
                                                     'intermediate links from paths')

    arg_parser.add_argument('-n',
                            '--network',
                            help='Location of the network.xml file',
                            required=True)

    arg_parser.add_argument('-s',
                            '--schedule',
                            help='Location of the schedule.xml file',
                            required=False,
                            default=None)

    arg_parser.add_argument('-v',
                            '--vehicles',
                            help='Location of the vehicles.xml file',
                            required=False,
                            default=None)

    arg_parser.add_argument('-p',
                            '--projection',
                            help='The projection network is in, eg. "epsg:27700"',
                            required=True)

    arg_parser.add_argument('-m',
                            '--simplification_map',
                            help='Suggested link ID map for simplification. JSON file that is read into a dictionary '
                                 'with keys that are link IDs in the network being passed and values that are new '
                                 'link ID strings. For example: `link_simp_map.json` file generated in a previous '
                                 'simplification attempt. This does not affect WHICH nodes are '
                                 'simplified, only the resulting link IDs if the IDs and simplification levels match. '
                                 'For any cases that do not match, new IDs will be generated.',
                            required=False,
                            default=None,
                            )

    arg_parser.add_argument('-np',
                            '--processes',
                            help='The number of processes to split computation across',
                            required=False,
                            default=1,
                            type=int)

    arg_parser.add_argument('-od',
                            '--output_dir',
                            help='Output directory for the simplified network',
                            required=True)

    args = vars(arg_parser.parse_args())
    network = args['network']
    schedule = args['schedule']
    vehicles = args['vehicles']
    projection = args['projection']
    simplification_map = args['simplification_map']
    processes = args['processes']
    output_dir = args['output_dir']
    ensure_dir(output_dir)

    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.WARNING)

    logging.info(f'Reading in network at {network}')
    n = read_matsim(
        path_to_network=network,
        epsg=projection,
        path_to_schedule=schedule,
        path_to_vehicles=vehicles
    )

    if simplification_map:
        logging.info(f'Reading suggested simplification map from {simplification_map}')
        with open(simplification_map) as json_file:
            simplification_map = json.load(json_file)

    logging.info('Simplifying the Network.')

    start = time.time()
    failed_suggested_ids = n.simplify(no_processes=processes, suggested_map=simplification_map)
    end = time.time()

    logging.info(
        f'Simplification resulted in {len(n.link_simplification_map)} links being simplified.')
    with open(os.path.join(output_dir, 'link_simp_map.json'), 'w', encoding='utf-8') as f:
        json.dump(n.link_simplification_map, f, ensure_ascii=False, indent=4)
    with open(os.path.join(output_dir, 'failed_suggested_simp_ids.json'), 'w', encoding='utf-8') as f:
        json.dump(
            {'failed_suggested_ids': list(failed_suggested_ids),
             'suggested_map': simplification_map},
            f, ensure_ascii=False, indent=4)

    n.write_to_matsim(output_dir)

    logging.info('Generating validation report')
    report = n.generate_validation_report()
    logging.info(f'Graph validation: {report["graph"]["graph_connectivity"]}')
    if n.schedule:
        logging.info(f'Schedule level validation: {report["schedule"]["schedule_level"]["is_valid_schedule"]}')
        logging.info(
            f'Schedule vehicle level validation: {report["schedule"]["vehicle_level"]["vehicle_definitions_valid"]}'
            )
        logging.info(f'Routing validation: {report["routing"]["services_have_routes_in_the_graph"]}')

    n.generate_standard_outputs(os.path.join(output_dir, 'standard_outputs'))

    logging.info(f'It took {round((end - start)/60, 3)} min to simplify the network.')
