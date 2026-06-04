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
        assert response.status_code in (401, 403), response.text
        assert response.json().get("error") == "APP_ID_MISSING"

    @allure.title("TestCommentNegative --> APP_ID_NOT_EXIST")
    def test_app_id_not_exist(self):
        response = self.api_comment.send_request(
            method="GET",
            url=self.api_comment.endpoint.get_list_comments(),
            params={"page": 0, "limit": 5},
            headers={"app-id": "invalid_app_id_value"},
            use_default_headers=False,
        )
        assert response.status_code in (401, 403), response.text
        assert response.json().get("error") == "APP_ID_NOT_EXIST"

    @allure.title("TestCommentNegative --> PARAMS_NOT_VALID (bad id)")
    @pytest.mark.parametrize("bad_comment_id", ["123", "not-an-id", "!!!!!!!!"])
    def test_params_not_valid_by_id(self, bad_comment_id: str):
        response = self.api_comment.send_request(
            method="DELETE",
            url=self.api_comment.endpoint.delete_comment(bad_comment_id),
        )
        assert response.status_code == 400, response.text
        assert response.json().get("error") == "PARAMS_NOT_VALID"

    @allure.title("TestCommentNegative --> bad pagination (400 or normalized 200)")
    @pytest.mark.parametrize("params", [{"page": -1, "limit": 10}, {"page": 0, "limit": 0}])
    def test_bad_pagination(self, params: dict):
        response = self.api_comment.send_request(
            method="GET",
            url=self.api_comment.endpoint.get_list_comments(),
            params=params,
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
        assert response_comment.status_code == 400, response_comment.text
        assert response_comment.json().get("error") == "BODY_NOT_VALID"

    @allure.title("TestCommentNegative --> RESOURCE_NOT_FOUND (valid id, not exists)")
    def test_resource_not_found_by_id(self):
        response = self.api_comment.send_request(
            method="DELETE",
            url=self.api_comment.endpoint.delete_comment("f" * 24),
        )
        assert response.status_code == 404, response.text
        assert response.json().get("error") == "RESOURCE_NOT_FOUND"

    @allure.title("TestCommentNegative --> PATH_NOT_FOUND")
    def test_path_not_found(self):
        list_url = self.api_comment.endpoint.get_list_comments()
        base = list_url.rsplit("/comment", 1)[0]

        response = self.api_comment.send_request(
            method="GET",
            url=f"{base}/wrong-path",
        )
        assert response.status_code == 404, response.text
        assert response.json().get("error") == "PATH_NOT_FOUND"
