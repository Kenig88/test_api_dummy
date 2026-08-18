import allure
import pytest

from config.base_test import BaseTest
from services.comment.comment_payload import CommentPayload


@allure.epic("Administration")
@allure.feature("Comment")
@pytest.mark.negative
class TestCommentNegative(BaseTest):
    @allure.title("TestCommentNegative --> APP_ID_MISSING")
    def test_app_id_missing(self):
        response = self.api_comment.send_request(
            method="GET",
            url=self.api_comment.endpoint.get_list_comments(),
            params={"page": 0, "limit": 5},
            use_default_headers=False,
        )
        self.api_comment.assert_error_response(response, 403, "APP_ID_MISSING")

    @allure.title("TestCommentNegative --> APP_ID_NOT_EXIST")
    def test_app_id_not_exist(self):
        response = self.api_comment.send_request(
            method="GET",
            url=self.api_comment.endpoint.get_list_comments(),
            params={"page": 0, "limit": 5},
            headers={"app-id": "invalid_app_id_value"},
            use_default_headers=False,
        )
        self.api_comment.assert_error_response(response, 403, "APP_ID_NOT_EXIST")

    @allure.title("TestCommentNegative --> PARAMS_NOT_VALID (bad id)")
    @pytest.mark.parametrize("bad_comment_id", ["123", "not-an-id", "!!!!!!!!"])
    def test_params_not_valid_by_id(self, bad_comment_id: str):
        response = self.api_comment.send_request(
            method="DELETE",
            url=self.api_comment.endpoint.delete_comment(bad_comment_id),
        )
        self.api_comment.assert_error_response(response, 400, "PARAMS_NOT_VALID")

    @allure.title("TestCommentNegative --> out-of-range pagination is normalized")
    @pytest.mark.parametrize(
        ("page", "limit", "expected_page", "expected_limit"),
        [
            pytest.param(-1, 10, 0, 10, id="negative-page"),
            pytest.param(0, 0, 0, 5, id="limit-below-minimum"),
        ],
    )
    def test_bad_pagination(self, page: int, limit: int, expected_page: int, expected_limit: int):
        response = self.api_comment.get_list_comments(
            page=page,
            limit=limit,
        )
        assert response.page == expected_page
        assert response.limit == expected_limit
        assert len(response.data) <= expected_limit

    @allure.title("TestCommentNegative --> BODY_NOT_VALID (create missing required field)")
    @pytest.mark.parametrize("missing_key", ["owner", "post"])
    def test_body_not_valid_create_missing_required(self, missing_key: str, created_user, created_post):
        user = created_user()
        post = created_post(user_id=str(user.id))
        payload = CommentPayload.comment_create_payload(user_id=str(user.id), post_id=str(post.id))
        payload.pop(missing_key, None)

        response_comment = self.api_comment.send_request(
            method="POST",
            url=self.api_comment.endpoint.create_comment(),
            json=payload,
        )
        self.api_comment.assert_error_response(response_comment, 400, "BODY_NOT_VALID")

    @allure.title("TestCommentNegative --> RESOURCE_NOT_FOUND (valid id, not exists)")
    def test_resource_not_found_by_id(self):
        response = self.api_comment.send_request(
            method="DELETE",
            url=self.api_comment.endpoint.delete_comment("f" * 24),
        )
        self.api_comment.assert_error_response(response, 404, "RESOURCE_NOT_FOUND")

    @allure.title("TestCommentNegative --> PATH_NOT_FOUND")
    def test_path_not_found(self):
        list_url = self.api_comment.endpoint.get_list_comments()
        base = list_url.rsplit("/comment", 1)[0]

        response = self.api_comment.send_request(
            method="GET",
            url=f"{base}/wrong-path",
        )
        self.api_comment.assert_error_response(response, 404, "PATH_NOT_FOUND")
