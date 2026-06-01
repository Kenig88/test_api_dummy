import logging
import requests

logger = logging.getLogger(__name__)


class ApiBase:
    def __init__(self, http_session: requests.Session, timeout: int = 15):
        self.http_session = http_session
        self.timeout = timeout

    def _json(self, response: requests.Response) -> dict:
        try:
            return response.json()
        except ValueError:
            return {"text": response.text}

    def _check_status_code(self, response: requests.Response, ok_statuses: list[int]) -> dict:
        body = self._json(response)

        logger.info(
            "%s %s -> %s",
            response.request.method,
            response.url,
            response.status_code,
        )

        logger.debug("Response body: %s", body)

        assert response.status_code in ok_statuses, {
            "status": response.status_code,
            "url": str(response.url),
            "body": body
        }

        return body