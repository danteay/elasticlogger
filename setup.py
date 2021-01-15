"""Setup configuration for elasticlogger package"""

import setuptools

with open("README.md", "r") as fh:
    LONG_DESC = fh.read()

setuptools.setup(
    name="elasticlogger",
    version="1.1.0",
    author="Eduardo Aguilar",
    author_email="dante.aguilar41@gmail.com",
    description="Standardized json logger for easy implementation",
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/eduardoay/elasticlogger",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "python_json_logger",
        "elasticsearch",
        "urllib3",
        "certifi",
        "sentry-sdk",
    ],
)
