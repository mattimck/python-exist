#!/usr/bin/env python
"""Exist client

Usage:
  exist authorize --client_id=<client_id> --client_secret=<client_secret> [--config=<config_file>]
  exist user [--config=<config_file>]
  exist attributes [<attribute_name>] [--limit=<limit>] [--page=<page>] [--date_min=<date_min>] [--date_max=<date_max>] [--config=<config_file>]
  exist insights [<attribute_name>] [--limit=<limit>] [--page=<page>] [--date_min=<date_min>] [--date_max=<date_max>] [--config=<config_file>]
  exist averages [<attribute_name>] [--limit=<limit>] [--page=<page>] [--date_min=<date_min>] [--date_max=<date_max>] [--config=<config_file>]
  exist correlations [<attribute_name>] [--limit=<limit>] [--page=<page>] [--date_min=<date_min>] [--date_max=<date_max>] [--config=<config_file>]
  exist --version
  exist --help

Options:
  -h --help                        Show this screen.
  --version                        Show version.
  --client_id=<client_id>          App key of your Exist app.
  --client_secret=<client_secret>  App secret of your Exist app.
  --limit=<limit>                  Number of values to return per page. Optional, max is 100.
  --page=<page>                    Page index. Optional, default is 1.
  --date_min=<date_min>            Oldest date (inclusive) of results to be returned, in format YYYY-mm-dd. Optional.
  --date_max=<date_max>            Most recent date (inclusive) of results to be returned, in format YYYY-mm-dd. Optional.
  --config=<config_file>           Use the config file specified [default: ./exist.cfg]


"""
from __future__ import absolute_import

from docopt import docopt
from pprint import PrettyPrinter
from six.moves import configparser

from exist import __version__
from exist.auth import ExistAuth
from exist.exist import Exist


class ExistCli:
    def __init__(self, arguments):
        """
        Runs the command specified as an argument with the options specified
        """
        self.config_file = arguments['--config']
        self.config = configparser.ConfigParser()
        self.client_id = None
        self.client_secret = None
        self.access_token = None

        if arguments['authorize']:
            self.client_id = arguments['--client_id']
            self.client_secret = arguments['--client_secret']
            self.authorize()
        elif not arguments['--version'] and not arguments['--help']:
            try:
                # Fail if config file doesn't exist or is missing information
                self.read_config()
            except (IOError, configparser.NoOptionError,
                    configparser.NoSectionError):
                print('Missing config information, please run '
                      '"exist authorize"')
            else:
                # Everything is good! Get the requested resource(s)
                self.get_resource(arguments)

    def read_config(self):
        """ Read credentials from the config file """
        with open(self.config_file) as cfg:
            try:
                self.config.read_file(cfg)
            except AttributeError:  # Not python 3.X fallback
                self.config.readfp(cfg)
        self.client_id = self.config.get('exist', 'client_id')
        self.client_secret = self.config.get('exist', 'client_secret')
        self.access_token = self.config.get('exist', 'access_token')

    def write_config(self, access_token):
        """ Write credentials to the config file """
        self.config.add_section('exist')
        self.config.set('exist', 'client_id', self.client_id)
        self.config.set('exist', 'client_secret', self.client_secret)
        self.config.set('exist', 'access_token', access_token)
        with open(self.config_file, 'w') as cfg:
            self.config.write(cfg)
        print('Credentials written to %s' % self.config_file)

    def get_resource(self, arguments):
        """ Gets the resource requested in the arguments """
        attribute_name = arguments['<attribute_name>']
        limit = arguments['--limit']
        page = arguments['--page']
        date_min = arguments['--date_min']
        date_max = arguments['--date_max']

        exist = Exist(self.client_id, self.client_secret, self.access_token)

        if arguments['user']:
            result = exist.user()
        elif arguments['attributes']:
            result = exist.attributes(attribute_name, limit, page, date_min, date_max)
        elif arguments['insights']:
            result = exist.insights(attribute_name, limit, page, date_min, date_max)
        elif arguments['averages']:
            result = exist.averages(attribute_name, limit, page, date_min, date_max)
        elif arguments['correlations']:
            result = exist.correlations(attribute_name, limit, page, date_min, date_max)

        pp = PrettyPrinter(indent=4)
        if isinstance(result, list):
            pp.pprint([res.data for res in result])
        else:
            pp.pprint(result.data)

    def authorize(self):
        """
        Authorize a user using the browser and a CherryPy server, and write
        the resulting credentials to a config file.
        """

        # Thanks to the magic of docopts, I can be guaranteed to have a
        # a client_id and client_secret
        auth = ExistAuth(self.client_id, self.client_secret)
        auth.browser_authorize()

        # Write the authentication information to a config file for later use
        if auth.token:
            self.write_config(auth.token['access_token'])
        else:
            print('ERROR: We were unable to authorize to use the Exist API.')


def main():
    """ Parse the arguments and use them to create a ExistCli object """
    version = 'Python Exist %s' % __version__
    arguments = docopt(__doc__, version=version)
    ExistCli(arguments)


if __name__ == '__main__':
    """ Makes this file runnable with "python -m exist.cli" """
    main()
