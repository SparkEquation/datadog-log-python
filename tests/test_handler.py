import json
import logging
from unittest.mock import patch, call

from datadog_log.handler import DatadogLogHandler, ComparableRequest


@patch('urllib.request.urlopen')
def test_handler(mock_urlopen):
    mock_urlopen.return_value = None
    handler = DatadogLogHandler(
        api_key='any',
        source='tests',
        tags={'tag1': 'value1'},
        service='unit-tests',
    )
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)

    logger.error('This is an error')
    logger.info('This is an info')
    logger.warning('This is a warning')

    mock_urlopen.assert_has_calls([
        call(ComparableRequest(
            url='https://http-intake.logs.datadoghq.com/v1/input/any',
            headers={'content-type': 'application/json'},
            data=json.dumps({
                "message": "This is an error",
                "status": "ERROR",
                "ddsource": "tests",
                "ddtags": "tag1=value1",
                "service": "unit-tests",
            }).encode(),
        )),
        call(ComparableRequest(
            url='https://http-intake.logs.datadoghq.com/v1/input/any',
            headers={'content-type': 'application/json'},
            data=json.dumps({
                "message": "This is a warning",
                "status": "WARNING",
                "ddsource": "tests",
                "ddtags": "tag1=value1",
                "service": "unit-tests",
            }).encode(),
        )),
    ])
