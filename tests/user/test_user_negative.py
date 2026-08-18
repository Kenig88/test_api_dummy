import allure
import pytest

from config.base_test import BaseTest
from services.user.user_payloads import UserPayloads


@allure.epic("Administration")
@allure.feature("User")
@pytest.mark.negative
class TestUserNegative(BaseTest):
    # -------------------------------------------------APP_ID_MISSING---------------------------------------------------
    @allure.title("TestUserNegative --> APP_ID_MISSING")
    def test_app_id_missing(self):
        response = self.api_user.send_request(
            method="GET",
            url=self.api_user.endpoint.get_list_users(),
            params={"page": 0, "limit": 5},
            use_default_headers=False,
        )
        self.api_user.assert_error_response(response, 403, "APP_ID_MISSING")

    # -------------------------------------------------APP_ID_NOT_EXIST-------------------------------------------------
    @allure.title("TestUserNegative --> APP_ID_NOT_EXIST")
    def test_app_id_not_exist(self):
        response = self.api_user.send_request(
            method="GET",
            url=self.api_user.endpoint.get_list_users(),
            params={"page": 0, "limit": 5},
            headers={"app-id": "invalid_app_id_value"},
            use_default_headers=False,
        )
        self.api_user.assert_error_response(response, 403, "APP_ID_NOT_EXIST")

    # -------------------------------------------------PARAMS_NOT_VALID-------------------------------------------------
    @allure.title("TestUserNegative --> PARAMS_NOT_VALID (bad id)")
    @pytest.mark.parametrize("bad_user_id", ["123", "not-an-id", "!!!!!!!!"])
    def test_params_not_valid(self, bad_user_id: str):
        response = self.api_user.send_request(
            method="GET",
            url=self.api_user.endpoint.get_user_by_id(bad_user_id),
        )
        self.api_user.assert_error_response(response, 400, "PARAMS_NOT_VALID")

    @allure.title("TestUserNegative --> out-of-range pagination is normalized")
    @pytest.mark.parametrize(
        ("page", "limit", "expected_page", "expected_limit"),
        [
            pytest.param(-1, 10, 0, 10, id="negative-page"),
            pytest.param(0, 999, 0, 50, id="limit-above-maximum"),
        ],
    )
    def test_bad_pagination(self, page: int, limit: int, expected_page: int, expected_limit: int):
        response = self.api_user.get_list_users(
            page=page,
            limit=limit,
        )
        assert response.page == expected_page
        assert response.limit == expected_limit
        assert len(response.data) <= expected_limit

    # --------------------------------------------------BODY_NOT_VALID--------------------------------------------------
    @allure.title("TestUserNegative --> BODY_NOT_VALID (create missing required)")
    @pytest.mark.parametrize("missing_key", ["firstName", "lastName", "email"])
    def test_body_not_valid_create_missing_required(self, missing_key: str):
        payload = UserPayloads.create_user_payload()
        payload.pop(missing_key, None)

        response = self.api_user.send_request(
            method="POST",
            url=self.api_user.endpoint.create_user(),
            json=payload,
        )
        error = self.api_user.assert_error_response(response, 400, "BODY_NOT_VALID")
        assert error.data == {missing_key: f"Path `{missing_key}` is required."}

    # -----------------------------------------------RESOURCE_NOT_FOUND-------------------------------------------------
    @allure.title("TestUserNegative --> RESOURCE_NOT_FOUND (valid id, not exists)")
    def test_resource_not_found(self):
        response = self.api_user.send_request(
            method="GET",
            url=self.api_user.endpoint.get_user_by_id("f" * 24),
        )
        self.api_user.assert_error_response(response, 404, "RESOURCE_NOT_FOUND")

    # -------------------------------------------------PATH_NOT_FOUND---------------------------------------------------
    @allure.title("TestUserNegative --> PATH_NOT_FOUND")
    def test_path_not_found(self):
        list_url = self.api_user.endpoint.get_list_users()
        base = list_url.rsplit("/user", 1)[0]

        response = self.api_user.send_request(
            method="GET",
            url=f"{base}/wrong-path",
        )
        self.api_user.assert_error_response(response, 404, "PATH_NOT_FOUND")
