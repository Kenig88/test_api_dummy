import json
import logging
from typing import Any, ClassVar

import allure
import requests

logger = logging.getLogger(__name__)


class Helper:
    """Helper: безопасно прикрепляет API-запросы и ответы к Allure."""

    SENSITIVE_HEADERS: ClassVar[frozenset[str]] = frozenset({"app-id", "authorization"})

    def _mask_sensitive_headers(self, headers: Any) -> dict[str, str]:
        return {
            str(key): "***" if str(key).lower() in self.SENSITIVE_HEADERS else str(value)
            for key, value in dict(headers).items()
        }

    def _mask_sensitive_values(self, text: str, headers: Any) -> str:
        masked_text = text

        for key, value in dict(headers).items():
            if str(key).lower() in self.SENSITIVE_HEADERS and value:
                masked_text = masked_text.replace(str(value), "***")

        return masked_text

    def _format_request_body(self, body: Any) -> str:
        if body is None:
            return "<empty>"

        if isinstance(body, bytes):
            body = body.decode("utf-8", errors="replace")

        if not isinstance(body, str):
            return str(body)

        try:
            return json.dumps(json.loads(body), indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            return body

    def _format_response_body(self, response: requests.Response) -> str:
        try:
            return json.dumps(
                response.json(),
                indent=2,
                ensure_ascii=False,
            )
        except ValueError:
            return response.text

    def attach_response_safe(self, response: requests.Response) -> None:
        """
        Прикрепляет к Allure краткую информацию об API-запросе и ответе.

        Метод не должен ломать тесты и защищает от повторного прикрепления
        одного и того же response.
        """
        if getattr(response, "_allure_attached", False):
            return

        try:
            request = response.request
            headers = self._mask_sensitive_headers(request.headers)
            request_body = self._format_request_body(request.body)
            request_body = self._mask_sensitive_values(request_body, request.headers)

            allure.attach(
                (
                    f"{request.method} {request.url}\n\n"
                    f"Headers:\n{json.dumps(headers, indent=2, ensure_ascii=False)}\n\n"
                    f"Body:\n{request_body}"
                ),
                name="Request",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception:  # Reporting must never break an API test.
            logger.debug("Could not attach request to Allure", exc_info=True)

        try:
            allure.attach(
                (
                    f"Status code: {response.status_code}\n"
                    f"Response time: {response.elapsed.total_seconds():.3f} sec\n\n"
                    f"Body:\n{self._format_response_body(response)}"
                ),
                name="Response",
                attachment_type=allure.attachment_type.TEXT,
            )
            response._allure_attached = True
        except Exception:  # Reporting must never break an API test.
            logger.debug("Could not attach response to Allure", exc_info=True)

    def attach_transport_error_safe(
        self,
        method: str,
        url: str,
        timeout: Any,
        error: requests.RequestException,
    ) -> None:
        """Прикрепляет transport error, не влияя на исход самого теста."""
        try:
            allure.attach(
                (f"{method.upper()} {url}\nTimeout: {timeout!r}\nError: {type(error).__name__}: {error}"),
                name="Transport error",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception:  # Reporting must never hide the original request error.
            logger.debug("Could not attach transport error to Allure", exc_info=True)
