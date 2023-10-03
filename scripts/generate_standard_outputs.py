import argparse
import logging
import os

from genet import read_matsim
from genet.utils.persistence import ensure_dir

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Generate Standard outputs for a network and/or schedule')

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

    arg_parser.add_argument('-od',
                            '--output_dir',
                            help='Output directory for the outputs',
                            required=True)

    args = vars(arg_parser.parse_args())
    network = args['network']
    schedule = args['schedule']
    vehicles = args['vehicles']
    projection = args['projection']
    output_dir = args['output_dir']
    ensure_dir(output_dir)

    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.WARNING)

    logging.info('Reading in network at {}'.format(network))
    if schedule:
        logging.info(f'Reading in schedule at {schedule}')
        if vehicles:
            logging.info(f'Reading in vehicles at {vehicles}')
        else:
            logging.info('No vehicles file given with the Schedule, vehicle types will be based on the default.')
    n = read_matsim(
        path_to_network=network,
        epsg=projection,
        path_to_schedule=schedule,
        path_to_vehicles=vehicles
    )

    logging.info('Generating standard outputs')
    n.generate_standard_outputs(os.path.join(output_dir))
