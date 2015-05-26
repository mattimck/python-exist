#!/usr/bin/env python
"""Exist client

Usage:
  exist authorize [--client_id=<client_id> --client_secret=<client_secret> | --api_token=<token> | --username=<username> --password=<password>] [--redirect_uri=<redirect_uri>] [--config=<config_file>]
  exist refresh_auth_token [--config=<config_file>]
  exist acquire_attributes [<attribute:value> <attribute:value>...] [--config=<config_file>]
  exist release_attributes [<attribute_name> <attribute_name>...] [--config=<config_file>]
  exist owned_attributes [--config=<config_file>]
  exist update_attributes [<attribute:date:value> <attribute:date:value>...] [--config=<config_file>]
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
import json

from docopt import docopt
from pprint import PrettyPrinter
from six.moves import configparser

from exist import __version__
from exist.auth import ExistAuth, ExistAuthBasic
from exist.exist import Exist


class ExistCli:
    def __init__(self, arguments):
        """
        Runs the command specified as an argument with the options specified
        """
        self.config_file = arguments.get('--config', 'exist.cfg')
        self.config = configparser.ConfigParser()
        self.client_id = None
        self.client_secret = None
        self.access_token = None
        self.redirect_uri = arguments['--redirect_uri']

        if arguments['authorize']:
            # check which type of authorization we are trying for
            if arguments['--username'] and arguments['--password']:
                # username and password provided
                self.authorize(username=arguments['--username'], password=arguments['--password'])
            elif arguments['--api_token']:
                # a predetermined token provided
                self.authorize(api_token=arguments['--api_token'])
            else:
                # OAuth credentials provided
                self.client_id = arguments['--client_id']
                self.client_secret = arguments['--client_secret']
                self.authorize()
        elif not arguments['--version'] and not arguments['--help']:
            try:
                # try to read existing config file, if it exists
                self.read_config()
            except (IOError, configparser.NoOptionError,
                    configparser.NoSectionError):
                print('Missing config information, please run '
                      '"exist authorize"')
            else:
                if arguments['refresh_auth_token']:
                    self.refresh_token(arguments)
                else:
                    self.get_resource(arguments)

    def read_config(self):
        """ Read credentials from the config file """
        with open(self.config_file) as cfg:
            try:
                self.config.read_file(cfg)
            except AttributeError:
                self.config.readfp(cfg)

        self.client_id = self.config.get('exist', 'client_id')
        self.client_secret = self.config.get('exist', 'client_secret')
        self.access_token = self.config.get('exist', 'access_token')

    def write_config(self, access_token):
        """ Write credentials to the config file """
        self.config.add_section('exist')

        # TODO: config is reading 'None' as string during authorization, so clearing this out
        # if no id or secret is set - need to fix this later
        if self.client_id:
            self.config.set('exist', 'client_id', self.client_id)
        else:
            self.config.set('exist', 'client_id', '')

        if self.client_secret:
            self.config.set('exist', 'client_secret', self.client_secret)
        else:
            self.config.set('exist', 'client_secret', '')

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

        # feed in the config we have, and let the Exist class figure out the best
        # way to authenticate
        exist = Exist(self.client_id, self.client_secret, self.access_token)

        # TODO: Tidy this up since we are repeating ourselves a lot below
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
        elif arguments['acquire_attributes']:
            attributes_dict = [{'name': x.split(':')[0], 'active': x.split(':')[1]} for x in arguments['<attribute:value>']]
            result = exist.arquire_attributes(attributes_dict)
        elif arguments['release_attributes']:
            attributes_dict = [{'name': x} for x in arguments['<attribute_name>']]
            result = exist.release_attributes(attributes_dict)
        elif arguments['owned_attributes']:
            result = exist.owned_attributes()
        elif arguments['update_attributes']:
            attributes_dict = [{'name': x.split(':')[0], 'date': x.split(':')[1], 'value': x.split(':')[2]} for x in arguments['<attribute:date:value>']]
            result = exist.update_attributes(attributes_dict)

        pp = PrettyPrinter(indent=4)
        if isinstance(result, list):
            pp.pprint([res.data for res in result])
        else:
            pp.pprint(result.data)

    def authorize(self, api_token=None, username=None, password=None):
        """
        Authorize a user using the browser and a CherryPy server, and write
        the resulting credentials to a config file.
        """

        access_token = None

        if username and password:
            # if we have a username and password, go and collect a token
            auth = ExistAuthBasic(username, password)
            auth.authorize()
            if auth.token:
                access_token = auth.token['access_token']
        elif api_token:
            # if we already have a token, just use that
            access_token = api_token
        else:
            # if we have a client_id and client_secret, we need to
            # authorize through the browser
            auth = ExistAuth(self.client_id, self.client_secret, 'code', self.redirect_uri)
            auth.browser_authorize()
            if auth.token:
                access_token = auth.token['access_token']

        # store the access token in the config file
        if access_token:
            self.write_config(access_token)
        else:
            print('ERROR: We were unable to authorize to use the Exist API.')

    def refresh_token(self, arguments):
        """
        Refresh a user's access token, using existing the refresh token previously
        received in the auth flow.
        """

        new_access_token = None

        auth = ExistAuth(self.client_id, self.client_secret)
        resp = auth.refresh_token(self.access_token)
        if auth.token:
            new_access_token = auth.token['access_token']
            print('OAuth token refreshed: %s' % new_access_token)
            self.write_config(new_access_token)
        else:
            print('ERROR: We were unable to refresh the OAuth token | %s' % json.dumps(resp))


def main():
    """ Parse the arguments and use them to create a ExistCli object """
    version = 'Python Exist %s' % __version__
    arguments = docopt(__doc__, version=version)
    ExistCli(arguments)


if __name__ == '__main__':
    """ Makes this file runnable with "python -m exist.cli" """
    main()
