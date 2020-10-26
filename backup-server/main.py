#!/usr/bin/env python3

import logging
import os

from backup_server.backup_server import BackupServer


def parse_config_params():
    """ Parse env variables to find program config params

	Function that search and parse program configuration parameters in the
	program environment variables. If at least one of the config parameters
	is not found a KeyError exception is thrown. If a parameter could not
	be parsed, a ValueError is thrown. If parsing succeeded, the function
	returns a map with the env variables
	"""
    config_params = {}
    try:
        config_params["backup_requests_port"] = int(os.environ["BACKUP_REQUESTS_PORT"])
        config_params["listen_backlog"] = int(os.environ["SERVER_LISTEN_BACKLOG"])
        config_params["node_register_port"] = int(os.environ["NODE_REGISTER_PORT"])
        config_params["backup_info_port"] = int(os.environ["BACKUP_INFO_PORT"])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting backup_server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting backup_server".format(e))

    return config_params


def main():
    initialize_log()
    config_params = parse_config_params()

    server = BackupServer(config_params["backup_requests_port"], config_params["listen_backlog"],
                          config_params["node_register_port"], config_params["backup_info_port"],
                          config_params["thread_pool_size"])
    server.run()


def initialize_log():
    """
	Python custom logging initialization

	Current timestamp is added to be able to identify in docker
	compose logs the date when the log has arrived
	"""
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )


if __name__ == "__main__":
    main()
