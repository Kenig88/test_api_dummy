import requests


class ApiBase:

    def _json(self, response: requests.Response) -> dict:
        try:
            return response.json()
        except ValueError:
            return {"text": response.text}

    def _check_status_code(self, response: requests.Response, ok_statuses: list[int]) -> dict:
        body = self._json(response)
        assert response.status_code in ok_statuses, body
        return body
