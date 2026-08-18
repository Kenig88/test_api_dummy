import logging
from collections.abc import Sequence
from typing import Any

import requests

from services.error_models import ErrorResponseModel
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

        if not use_default_headers:
            headers = dict(kwargs.pop("headers", {}) or {})
            headers.setdefault("app-id", None)
            headers.setdefault("Accept", None)
            headers.setdefault("Content-Type", None)
            kwargs["headers"] = headers

        try:
            response = self.http_session.request(method=method, url=url, **kwargs)
        except requests.RequestException as error:
            logger.exception(
                "%s %s -> %s",
                method.upper(),
                url,
                type(error).__name__,
            )
            self.attach_transport_error_safe(
                method=method,
                url=url,
                timeout=kwargs.get("timeout"),
                error=error,
            )
            raise

        self.attach_response_safe(response)

        logger.info(
            "%s %s -> %s",
            response.request.method,
            response.url,
            response.status_code,
        )

        return response

    def _check_status_code(self, response: requests.Response, ok_statuses: Sequence[int]) -> Any:
        body = self._json(response)

        assert response.status_code in ok_statuses, {
            "status": response.status_code,
            "url": str(response.url),
            "body": body,
        }

        return body

    def assert_error_response(
        self,
        response: requests.Response,
        expected_status: int,
        expected_error: str,
    ) -> ErrorResponseModel:
        body = self._check_status_code(response, ok_statuses=[expected_status])
        error = ErrorResponseModel.model_validate(body)

        assert error.error == expected_error, {
            "expected_error": expected_error,
            "actual_error": error.error,
            "status": response.status_code,
            "url": str(response.url),
            "body": body,
        }

        return error
