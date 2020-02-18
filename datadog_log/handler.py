import json
import logging
from typing import Dict
from urllib import request


class ComparableRequest(request.Request):

    def __eq__(self, other: 'ComparableRequest') -> bool:
        return (
            isinstance(other, ComparableRequest)
            and self.full_url == other.full_url
            and self.headers == other.headers
            and self.data == other.data
        )

    def __repr__(self) -> str:
        return f'<Request {self.data.decode()}>'


class DatadogLogHandler(logging.Handler):
    def __init__(self,
                 api_key: str,
                 hostname: str = None,
                 source: str = None,
                 tags: Dict[str, str] = None,
                 service: str = None,
                 base_url: str = 'https://http-intake.logs.datadoghq.com/v1/input/',
                 *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._api_key = api_key
        self._hostname = hostname
        self._source = source
        self._tags = tags
        self._service = service
        self._base_url = base_url

    def emit(self, record: logging.LogRecord) -> None:
        text = self.format(record)
        data = {
            'message': text,
            'status': record.levelname,
        }
        if self._hostname is not None:
            data['hostname'] = self._hostname
        if self._source is not None:
            data['ddsource'] = self._source
        if self._tags is not None:
            data['ddtags'] = ','.join(f'{k}={v}' for k, v in self._tags.items())
        if self._service is not None:
            data['service'] = self._service
        req = ComparableRequest(
            url=self._base_url + self._api_key,
            data=json.dumps(data).encode(),
            headers={'content-type': 'application/json'},
        )
        request.urlopen(req)
