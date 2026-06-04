import logging
from typing import Any

import requests

from utils.helper import Helper

logger = logging.getLogger(__name__)


class ApiBase(Helper):
    def __init__(self, http_session: requests.Session, timeout: int = 15):
        self.http_session = http_session
        self.timeout = timeout

    def _json(self, response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return {"text": response.text}

    def send_request(
        self,
        method: str,
        url: str,
        use_default_headers: bool = True,
        **kwargs: Any,
    ) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)

        requester = self.http_session.request if use_default_headers else requests.request
        response = requester(method=method, url=url, **kwargs)

        self.attach_response_safe(response)

        logger.info(
            "%s %s -> %s",
            response.request.method,
            response.url,
            response.status_code,
        )

        return response

    def _check_status_code(self, response: requests.Response, ok_statuses: list[int]) -> Any:
        body = self._json(response)

        assert response.status_code in ok_statuses, {
            "status": response.status_code,
            "url": str(response.url),
            "body": body,
        }

        return body
