"""Custom Json Encoder for default serialization"""

import json

from elasticsearch import JSONSerializer


class ElasticJSONEncoder(JSONSerializer):
    """Custom JSON serializer for Elasticsearch integration"""

    mimetype = "application/json"

    def default(self, data):
        try:
            return super().default(data)
        except TypeError as err:
            try:
                return str(data)
            except Exception as err2:
                raise err2 from err


class LoggerJSONEncoder(json.JSONEncoder):
    """Custom JSON serializer for logging"""

    def default(self, o):
        """
        Default object serialization
        :param o: Object data
        :return: string result
        """

        return str(o)
