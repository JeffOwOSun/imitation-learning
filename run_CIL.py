import argparse
import logging
import sys

from carla.benchmarks.corl_2017 import CoRL2017

from carla.tcp import TCPConnectionError
from carla.client import make_carla_client
from agents.imitation.imitation_learning import ImitationLearning
import time

try:
    from carla import carla_server_pb2 as carla_protocol
except ImportError:
    raise RuntimeError('cannot import "carla_server_pb2.py", run the protobuf compiler to generate this file')

if (__name__ == '__main__'):

    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='localhost',
        help='IP of the host server (default: localhost)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-c', '--city-name',
        metavar='C',
        default='Town01',
        help='The town that is going to be used on benchmark'
             + '(needs to match active town in server, options: Town01 or Town02)')
    argparser.add_argument(
        '-n', '--log_name',
        metavar='T',
        default='test',
        help='The name of the log file to be created by the scripts'
    )

    argparser.add_argument(
         '--avoid-stopping',
        action='store_true',
        help=' Uses the speed prediction branch to avoid unwanted agent stops'
    )

    args = argparser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)

    agent = ImitationLearning(args.city_name,args.avoid_stopping)

    while True:
        try:

            with make_carla_client(args.host, args.port) as client:
                corl = CoRL2017(args.city_name, args.log_name,
                        continue_experiment=True)
                results = corl.benchmark_agent(agent, client)
                corl.plot_summary_test()
                corl.plot_summary_train()

                break

        except TCPConnectionError as error:
            logging.error(error)
            time.sleep(1)
        except Exception as exception:
            logging.exception(exception)
            sys.exit(1)
