import allure
import pytest

from config.base_test import BaseTest
from services.post.post_payload import PostPayload


@allure.epic("Administration")
@allure.feature("Post")
@pytest.mark.negative
class TestPostNegative(BaseTest):
    # -------------------------------------------------APP_ID_MISSING---------------------------------------------------
    @allure.title("TestPostNegative --> APP_ID_MISSING")
    def test_app_id_missing(self):
        response = self.api_post.send_request(
            method="GET",
            url=self.api_post.endpoint.get_list_posts(),
            params={"page": 0, "limit": 5},
            use_default_headers=False,
        )
        self.api_post.assert_error_response(response, 403, "APP_ID_MISSING")

    # -------------------------------------------------APP_ID_NOT_EXIST-------------------------------------------------
    @allure.title("TestPostNegative --> APP_ID_NOT_EXIST")
    def test_app_id_not_exist(self):
        response = self.api_post.send_request(
            method="GET",
            url=self.api_post.endpoint.get_list_posts(),
            params={"page": 0, "limit": 5},
            headers={"app-id": "invalid_app_id_value"},
            use_default_headers=False,
        )
        self.api_post.assert_error_response(response, 403, "APP_ID_NOT_EXIST")

    # -------------------------------------------------PARAMS_NOT_VALID-------------------------------------------------
    @allure.title("TestPostNegative --> PARAMS_NOT_VALID (bad id)")
    @pytest.mark.parametrize("bad_post_id", ["123", "not-an-id", "!!!!!!!!!!"])
    def test_params_not_valid_by_id(self, bad_post_id: str):
        response = self.api_post.send_request(
            method="GET",
            url=self.api_post.endpoint.get_post_by_post_id(bad_post_id),
        )
        self.api_post.assert_error_response(response, 400, "PARAMS_NOT_VALID")

    @allure.title("TestPostNegative --> out-of-range pagination is normalized")
    @pytest.mark.parametrize(
        ("page", "limit", "expected_page", "expected_limit"),
        [
            pytest.param(-1, 10, 0, 10, id="negative-page"),
            pytest.param(0, 999, 0, 50, id="limit-above-maximum"),
        ],
    )
    def test_bad_pagination(self, page: int, limit: int, expected_page: int, expected_limit: int):
        response = self.api_post.get_list_posts(
            page=page,
            limit=limit,
        )
        assert response.page == expected_page
        assert response.limit == expected_limit
        assert len(response.data) <= expected_limit

    # --------------------------------------------------BODY_NOT_VALID--------------------------------------------------
    @allure.title("TestPostNegative --> BODY_NOT_VALID (create missing owner)")
    def test_body_not_valid_create_missing_owner(self, created_user):
        user = created_user()
        payload = PostPayload.create_post_payload(user_id=str(user.id))
        payload.pop("owner", None)

        response_post = self.api_post.send_request(
            method="POST",
            url=self.api_post.endpoint.create_post(),
            json=payload,
        )
        self.api_post.assert_error_response(response_post, 400, "BODY_NOT_VALID")

    # -----------------------------------------------RESOURCE_NOT_FOUND-------------------------------------------------
    @allure.title("TestPostNegative --> RESOURCE_NOT_FOUND (valid id, not exists)")
    def test_resource_not_found_by_id(self):
        response = self.api_post.send_request(
            method="GET",
            url=self.api_post.endpoint.get_post_by_post_id("f" * 24),
        )
        self.api_post.assert_error_response(response, 404, "RESOURCE_NOT_FOUND")

    # -------------------------------------------------PATH_NOT_FOUND---------------------------------------------------
    @allure.title("TestPostNegative --> PATH_NOT_FOUND")
    def test_path_not_found(self):
        list_url = self.api_post.endpoint.get_list_posts()
        base = list_url.rsplit("/", 1)[0]

        response = self.api_post.send_request(
            method="GET",
            url=f"{base}/wrong-path",
        )
        self.api_post.assert_error_response(response, 404, "PATH_NOT_FOUND")
