import arrow
import json
import slumber
import sys

from oauthlib.oauth2 import Client
from requests_oauthlib import OAuth2
from slumber.exceptions import HttpClientError, HttpServerError
from slumber.serialize import Serializer, JsonSerializer

from .auth import ExistAuthKey
from .exceptions import ExistException, ExistHttpException

BASE_URL = 'https://exist.io/'
API_URL = BASE_URL + 'api/'
OAUTH_URL = BASE_URL + 'oauth2/'


class ExistSerializer(JsonSerializer):
    """ Override the built-in JSON serializer to handle bytes """
    def loads(self, data):
        return json.loads(data.decode('utf8'))


class Exist:
    def __init__(self, client_id, client_secret, access_token, user_id=None):

        # check if we are using OAuth or just the basic token api
        if client_id:
            auth = OAuth2(client_id, Client(client_id),
                          {'access_token': access_token})
        else:
            auth = ExistAuthKey(access_token)

        user = user_id if user_id else '$self'

        s = Serializer(default="json", serializers=[ExistSerializer()])

        self.read_api = slumber.API('%s1/users/%s/' % (API_URL, user), auth=auth, serializer=s)
        self.update_api = slumber.API('%s1/' % (API_URL), auth=auth, serializer=s)

    def user(self):
        return ExistUser(self._get_object(self.read_api.today))

    def attributes(self, attribute_name=None, limit=None, page=None, date_min=None, date_max=None):
        if attribute_name:
            attribute_object = self._get_object(self.read_api.attributes, attribute_name, **{'limit': limit, 'page': page, 'date_min': date_min, 'date_max': date_max})
            return ExistAttribute(attribute_object)

        attributes = self._get_object(self.read_api.attributes)
        return [ExistAttribute(attribute) for attribute in attributes]

    def insights(self, attribute_name=None, limit=None, page=None, date_min=None, date_max=None):
        if attribute_name:
            attribute_insight = self._get_object(self.read_api.insights.attribute, attribute_name, **{'limit': limit, 'page': page, 'date_min': date_min, 'date_max': date_max})
            return ExistAttributeInsight(attribute_insight)

        return ExistInsight(self._get_object(self.read_api.insights))

    def averages(self, attribute_name=None, limit=None, page=None, date_min=None, date_max=None):
        if attribute_name:
            attribute_object = self._get_object(self.read_api.averages.attribute, attribute_name, **{'limit': limit, 'page': page, 'date_min': date_min, 'date_max': date_max})
            return ExistAttributeAverage(attribute_object)

        averages = self._get_object(self.read_api.averages)
        return [ExistAverage(average) for average in averages]

    def correlations(self, attribute_name=None, limit=None, page=None, date_min=None, date_max=None):
        attribute_object = self._get_object(self.read_api.correlations.attribute, attribute_name, **{'limit': limit, 'page': page, 'date_min': date_min, 'date_max': date_max})
        return ExistAttributeCorrelation(attribute_object)

    def _get_object(self, api_section, object_id=None, **kwargs):
        try:
            args = (object_id,) if object_id else tuple()
            return api_section(*args).get(**kwargs)
        except (HttpClientError, HttpServerError):
            ExistHttpException.build_exception(sys.exc_info()[1])


class UnicodeMixin(object):
    if sys.version_info > (3, 0):
        __str__ = lambda x: x.__unicode__()
    else:
        __str__ = lambda x: unicode(x).encode('utf-8')


class ExistObject(UnicodeMixin):
    def __init__(self, data):
        self.data = data
        for name, value in self.data.items():
            self.set_value(name, value)

    def set_value(self, name, value):
        if name in ['date', 'datetime', 'startTime', 'Timestamp']:
            setattr(self, name, arrow.get(value))
        else:
            setattr(self, name, value)

    def __unicode__(self):
        return '%s: %s' % (type(self), json.dumps(self.data))


class ExistUser(ExistObject):
    pass


class ExistAttribute(ExistObject):
    pass


class ExistAttributeAverage(ExistObject):
    def __init__(self, data):
        super(ExistAttributeAverage, self).__init__(data)
        average_results = []
        for result in self.results:
            average_results.append(ExistAttributeAverageDetail(result))
        self.results = average_results


class ExistAttributeAverageDetail(ExistObject):
    pass


class ExistAttributeInsight(ExistObject):
    def __init__(self, data):
        super(ExistAttributeInsight, self).__init__(data)
        insight_results = []
        for result in self.results:
            insight_results.append(ExistAttributeInsightDetail(result))
        self.results = insight_results


class ExistAttributeInsightDetail(ExistObject):
    pass


class ExistAttributeCorrelation(ExistObject):
    def __init__(self, data):
        super(ExistAttributeCorrelation, self).__init__(data)
        correlation_results = []
        for result in self.results:
            correlation_results.append(ExistCorrelation(result))
        self.results = correlation_results


class ExistCorrelation(ExistObject):
    pass


class ExistInsight(ExistObject):
    pass


class ExistAverage(ExistObject):
    pass
