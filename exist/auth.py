from __future__ import absolute_import

import cherrypy
import json
import os
import requests
import sys
import threading
import traceback
import webbrowser

from oauthlib.oauth2.rfc6749.errors import (
    MismatchingStateError,
    MissingTokenError
)

from oauthlib.oauth2 import Client
from requests_oauthlib import OAuth2, OAuth2Session
from requests.auth import AuthBase

# TODO: These are doubled up in exist.py - put them in central location to import from
BASE_URL = 'https://exist.io/'
API_URL = BASE_URL + 'api/'
OAUTH_URL = BASE_URL + 'oauth2/'


class ExistAuthKey(AuthBase):
    def __init__(self, apikey):
        self.apikey = apikey

    def __call__(self, r):
        r.headers['Authorization'] = "Token %s" % self.apikey
        return r


class ExistAuthBasic:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None

    def authorize(self):
        response = requests.post(API_URL+'1/auth/simple-token/', {'username': self.username, 'password': self.password})
        json_resp = json.loads(response.content)
        self.token = {'access_token': json_resp['token']}


class ExistAuth:
    def __init__(self, client_id, client_secret,
                 response_type='code',
                 redirect_uri='http://127.0.0.1:8080/', state=None,
                 scope=['read+write'], success_html=None,
                 failure_html=None):
        """ Initialize the OAuth2Session """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.success_html = success_html if success_html else """
            <h1>You are now authorized to access the Exist API!</h1>
            The access_token is: %s
            <br/><h3>You can close this window</h3>"""
        self.failure_html = failure_html if failure_html else """
            <h1>ERROR: %s</h1><br/><h3>You can close this window</h3>%s"""
        # Ignore when the Exist API doesn't return the actual scope granted,
        # even though this goes against rfc6749:
        #     https://github.com/idan/oauthlib/blob/master/oauthlib/oauth2/rfc6749/parameters.py#L392
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = 'true'
        self.token = None
        self.state = state
        self.oauth = OAuth2Session(
            self.client_id, scope=self.scope, redirect_uri=self.redirect_uri,
            state=self.state)

    def authorize_url(self):
        """
        Build the authorization url and save the state. Return the
        authorization url
        """
        url, self.state = self.oauth.authorization_url(
            '%sauthorize' % OAUTH_URL)
        return url

    def fetch_token(self, code, state):
        """
        Fetch the token, using the verification code. Also, make sure the state
        received in the response matches the one in the request. Returns the
        access_token.
        """
        if self.state != state:
            raise MismatchingStateError()
        self.token = self.oauth.fetch_token(
            '%saccess_token/' % OAUTH_URL, code=code,
            client_secret=self.client_secret)
        return self.token['access_token']

    def refresh_token(self, refresh_token):
        """
        Get a new token, using the provided refresh token. Returns the new
        access_token.
        """

        response = requests.post('%saccess_token' % OAUTH_URL, {
                                 'refresh_token': refresh_token,
                                 'grant_type': 'refresh_token',
                                 'client_id': self.client_id,
                                 'client_secret': self.client_secret
                                 })
        resp = json.loads(response.content)

        if 'access_token' in resp:
            self.token = resp['access_token']

        return resp

    def browser_authorize(self):
        """
        Open a browser to the authorization url and spool up a CherryPy
        server to accept the response
        """
        url = self.authorize_url()
        # Open the web browser in a new thread for command-line browser support
        threading.Timer(1, webbrowser.open, args=(url,)).start()

        server_config = {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 443,

            'server.ssl_module': 'pyopenssl',
            'server.ssl_certificate': 'tests/files/certificate.cert',
            'server.ssl_private_key': 'tests/files/key.key',
        }

        cherrypy.config.update(server_config)
        cherrypy.quickstart(self)

    @cherrypy.expose(['connected'])
    def index(self, state, code=None, error=None):
        """
        Receive a Exist response containing a verification code. Use the code
        to fetch the access_token.
        """
        error = None
        if code:
            try:
                auth_token = self.fetch_token(code, state)
            except MissingTokenError:
                error = self._fmt_failure(
                    'Missing access token parameter.</br>Please check that '
                    'you are using the correct client_secret')
            except MismatchingStateError:
                error = self._fmt_failure('CSRF Warning! Mismatching state')
        else:
            error = self._fmt_failure('Unknown error while authenticating')
        # Use a thread to shutdown cherrypy so we can return HTML first
        self._shutdown_cherrypy()
        return error if error else self.success_html % (auth_token)

    def _fmt_failure(self, message):
        tb = traceback.format_tb(sys.exc_info()[2])
        tb_html = '<pre>%s</pre>' % ('\n'.join(tb)) if tb else ''
        return self.failure_html % (message, tb_html)

    def _shutdown_cherrypy(self):
        """ Shutdown cherrypy in one second, if it's running """
        if cherrypy.engine.state == cherrypy.engine.states.STARTED:
            threading.Timer(1, cherrypy.engine.exit).start()
