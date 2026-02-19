from utils.helper import Helper
import requests
import allure

from services.comment.comment_endpoints import CommentEndpoints


class ApiComment(Helper):
    def __init__(self, http_session: requests.Session, endpoints: CommentEndpoints, timeout: int = 15):
        self.http_session = http_session
        self.endpoint = endpoints
        self.timeout = timeout

    def _json(self, response: requests.Response):
        try:
            return response.json()
        except ValueError:
            return {"text": response.text}

    def _check_status_code(self, response: requests.Response, ok_statuses: list[int]) -> dict:
        body = self._json(response)
        assert response.status_code in ok_statuses, body
        return body

    # ----------------------------------------------------- CRUD -------------------------------------------------------
    # CRUD = Create, Read, Update, Delete (создать, прочитать, обновить, удалить), включая вызовы списков.
