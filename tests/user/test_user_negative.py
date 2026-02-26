import allure
import pytest
import requests

from config.base_test import BaseTest
from services.user.user_payloads import UserPayloads


@allure.epic("Administration")
@allure.feature("User")
@pytest.mark.negative
class TestUserNegative(BaseTest):

    # -------------------------------------------------APP_ID_MISSING---------------------------------------------------
    @allure.title("TestUserNegative --> APP_ID_MISSING")
    def test_app_id_missing(self):
        response = requests.get(
            url=self.api_user.endpoint.get_list_users(),
            params={"page": 0, "limit": 5},
            timeout=self.api_user.timeout
        )
        assert response.status_code in (401, 403), response.text
        assert response.json().get("error") == "APP_ID_MISSING"

    # -------------------------------------------------APP_ID_NOT_EXIST-------------------------------------------------
    @allure.title("TestUserNegative --> APP_ID_NOT_EXIST")
    def test_app_id_not_exist(self):
        response = requests.get(
            url=self.api_user.endpoint.get_list_users(),
            params={"page": 0, "limit": 5},
            headers={"app-id": "invalid_app_id_value"},
            timeout=self.api_user.timeout
        )
        assert response.status_code in (401, 403), response.text
        assert response.json().get("error") == "APP_ID_NOT_EXIST"

    # -------------------------------------------------PARAMS_NOT_VALID-------------------------------------------------
    @allure.title("TestUserNegative --> PARAMS_NOT_VALID (bad id)")
    @pytest.mark.parametrize("bad_user_id", ["123", "not-an-id", "!!!!!!!!"])
    def test_params_not_valid(self, bad_user_id: str):
        response = self.api_user.http_session.get(
            url=self.api_user.endpoint.get_user_by_id(bad_user_id),
            timeout=self.api_user.timeout
        )
        assert response.status_code == 400, response.text
        assert response.json().get("error") == "PARAMS_NOT_VALID"

    @allure.title("TestUserNegative --> bad pagination (400 or normalized 200)")
    @pytest.mark.parametrize("params", [{"page": -1, "limit": 10}, {"page": 0, "limit": 999}])
    def test_bad_pagination(self, params: dict):
        response = self.api_user.http_session.get(
            url=self.api_user.endpoint.get_list_users(),
            params=params,
            timeout=self.api_user.timeout
        )
        if response.status_code == 400:
            assert response.json().get("error") == "PARAMS_NOT_VALID"
        else:
            assert response.status_code == 200, response.text
            body = response.json()
            assert isinstance(body.get("data"), list)
            assert isinstance(body.get("page"), int)
            assert isinstance(body.get("limit"), int)
            assert len(body["data"]) <= body["limit"]

    # --------------------------------------------------BODY_NOT_VALID--------------------------------------------------
    @allure.title("TestUserNegative --> BODY_NOT_VALID (create missing required)")
    @pytest.mark.parametrize("missing_key", ["firstName", "lastName", "email"])
    def test_body_not_valid_create_missing_required(self, missing_key: str):
        payload = UserPayloads.create_user_payload()
        payload.pop(missing_key, None)

        response = self.api_user.http_session.post(
            url=self.api_user.endpoint.create_user(),
            json=payload,
            timeout=self.api_user.timeout
        )
        assert response.status_code == 400, response.text
        assert response.json().get("error") == "BODY_NOT_VALID"

    # -----------------------------------------------RESOURCE_NOT_FOUND-------------------------------------------------
    @allure.title("TestUserNegative --> RESOURCE_NOT_FOUND (valid id, not exists)")
    def test_resource_not_found(self):
        response = self.api_user.http_session.get(
            url=self.api_user.endpoint.get_user_by_id("f" * 24),
            timeout=self.api_user.timeout
        )
        assert response.status_code == 404, response.text
        assert response.json().get("error") == "RESOURCE_NOT_FOUND"

    # -------------------------------------------------PATH_NOT_FOUND---------------------------------------------------
    @allure.title("TestUserNegative --> PATH_NOT_FOUND")
    def test_path_not_found(self):
        list_url = self.api_user.endpoint.get_list_users()
        base = list_url.rsplit("/user", 1)[0]

        response = self.api_user.http_session.get(
            url=f"{base}/wrong-path",
            timeout=self.api_user.timeout
        )
        assert response.status_code == 404, response.text
        assert response.json().get("error") == "PATH_NOT_FOUND"
