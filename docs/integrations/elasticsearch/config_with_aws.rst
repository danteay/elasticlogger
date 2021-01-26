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

    region = 'us-east-1' # Change with your specific region
    service = 'es'
    credentials = Session().get_credentials()

    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        service,
        session_token=credentials.token
    )

    logger = Logger(name="test-logger", level=logging.INFO)

    logger.enable_elastic(
        url=os.getenv("ELASTICSEARCH_URL"),
        index=os.getenv("ELASTICSEARCH_INDEX"),
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )