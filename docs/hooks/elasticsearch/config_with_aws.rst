Config with AWS Elasticsearch service
=====================================

To use an Elasticsearch service hosted on AWS yo need to make the following configurations:

.. code-block:: python

    import os
    import logging

    from elasticsearch import RequestsHttpConnection
    from requests_aws4auth import AWS4Auth
    from boto3.session import Session

    from elasticlogger import Logger
    from elasticlogger.hooks.elasticsearch import ElasticSearch

    region = 'us-east-1' # Change with your specific region
    service = 'es'
    credentials = Session().get_credentials()

    aws_auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        service,
        session_token=credentials.token
    )

    es_hook = ElasticSearch(
        url=os.getenv("ELASTICSEARCH_URL"),
        index=os.getenv("ELASTICSEARCH_INDEX"),
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    logger = Logger("test-logger", hooks=[es_hook])