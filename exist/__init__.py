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
__author__ = 'Matt McDougall'
__author_email__ = 'matt@moatmedia.com.au'
__copyright__ = 'Copyright 2015 MoatMedia'
__license__ = 'Apache 2.0'
__version__ = '0.1.6'
__release__ = __version__
