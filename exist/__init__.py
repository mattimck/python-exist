"""
Exist API Python Client Implementation. Facilitates connection to Exist's
`REST API <http://developer.exist.io/>`_ and retrieving user data.
"""


from .exist import (
    API_URL,
    OAUTH_URL,
    Exist,
    ExistAttribute,
    ExistCorrelation,
    ExistInsight,
    ExistAverage,
)

__all__ = ['API_URL', 'OAUTH_URL', 'Exist', 'ExistAttribute',
           'ExistCorrelation', 'ExistInsight', 'ExistAverage']
__title__ = 'exist'
__author__ = 'Curo'
__author_email__ = 'matt@meetcuro.com'
__copyright__ = 'Copyright 2015 Curo'
__license__ = 'Apache 2.0'
__version__ = '0.1.0'
__release__ = __version__
