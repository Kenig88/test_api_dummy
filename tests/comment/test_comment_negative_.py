import allure
import pytest
import requests

from config.base_test import BaseTest
from services.comment.comment_payload import CommentPayload


@allure.epic("Administration")
@allure.feature("Comment")
@pytest.mark.negative
class TestCommentNegative(BaseTest):

    # -------------------------------------------------APP_ID_MISSING---------------------------------------------------
    @allure.title("TestCommentNegative --> APP_ID_MISSING")
    def test_app_id_missing(self):
        session = requests.Session()
        response = session.get(
            url=self.api_comment.endpoint.get_list_comments(),
            params={"page": 0, "limit": 5},
            timeout=self.api_comment.timeout
        )
        assert response.status_code in (401, 403), response.text
        assert response.json().get("error") == "APP_ID_MISSING"

    # -------------------------------------------------APP_ID_NOT_EXIST-------------------------------------------------
    @allure.title("TestCommentNegative --> APP_ID_NOT_EXIST")
    def test_app_id_not_exist(self):
        session = requests.Session()
        session.headers.update({"app-id": "invalid_app_id_value"})
        response = session.get(
            url=self.api_comment.endpoint.get_list_comments(),
            params={"page": 0, "limit": 5},
            timeout=self.api_comment.timeout
        )
        assert response.status_code in (401, 403), response.text
        assert response.json().get("error") == "APP_ID_NOT_EXIST"

    # -------------------------------------------------PARAMS_NOT_VALID-------------------------------------------------
    @allure.title("TestCommentNegative --> PARAMS_NOT_VALID (bad id)")
    @pytest.mark.parametrize("bad_comment_id", ["123", "not-an-id", "!!!!!!!!"])
    def test_params_not_valid_by_id(self, bad_comment_id: str):
        response = self.api_comment.http_session.delete(
            url=self.api_comment.endpoint.delete_comment(bad_comment_id),
            timeout=self.api_comment.timeout
        )
        assert response.status_code == 400, response.text
        assert response.json().get("error") == "PARAMS_NOT_VALID"

    @allure.title("TestCommentNegative --> bad pagination (400 or normalized 200)")
    @pytest.mark.parametrize("params", [{"page": -1, "limit": 10}, {"page": 0, "limit": 000}])
    def test_bad_pagination(self, params: dict):
        response = self.api_comment.http_session.get(
            url=self.api_comment.endpoint.get_list_comments(),
            params=params,
            timeout=self.api_comment.timeout
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
    @allure.title("TestCommentNegative --> BODY_NOT_VALID (create missing required field)")
    @pytest.mark.parametrize("missing_key", ["owner", "post"])
    def test_body_not_valid_create_missing_required(self, missing_key: str):
        # user_id
        response_user = self.api_user.http_session.get(
            url=self.api_user.endpoint.get_list_users(),
            params={"page": 0, "limit": 1},
            timeout=self.api_user.timeout
        )
        assert response_user.status_code == 200, response_user.text
        user_id = response_user.json()["data"][0]["id"]

        # post_id
        response_post = self.api_post.http_session.get(
            url=self.api_post.endpoint.get_list_posts(),
            params={"page": 0, "limit": 1},
            timeout=self.api_post.timeout
        )
        assert response_post.status_code == 200, response_post.text
        post_id = response_user.json()["data"][0]["id"]

        # работа с comment
        payload = CommentPayload.comment_create_payload(user_id=user_id, post_id=post_id)
        payload.pop(missing_key, None)

        response_comment = self.api_comment.http_session.post(
            url=self.api_comment.endpoint.create_comment(),
            json=payload,
            timeout=self.api_comment.timeout
        )
        assert response_comment.status_code == 400, response_comment.text
        assert response_comment.json().get("error") == "BODY_NOT_VALID"

    # -----------------------------------------------RESOURCE_NOT_FOUND-------------------------------------------------
    @allure.title("TestCommentNegative --> RESOURCE_NOT_FOUND (valid id, not exists)")
    def test_resource_not_found_by_id(self):
        response = self.api_comment.http_session.delete(
            url=self.api_comment.endpoint.delete_comment("f" * 24),
            timeout=self.api_comment.timeout
        )
        assert response.status_code == 404, response.text
        assert response.json().get("error") == "RESOURCE_NOT_FOUND"

    # -------------------------------------------------PATH_NOT_FOUND---------------------------------------------------
    @allure.title("TestCommentNegative --> PATH_NOT_FOUND")
    def test_path_not_found(self):
        list_url = self.api_comment.endpoint.get_list_comments()
        base = list_url.rsplit("/comment", 1)[0]

        response = self.api_comment.http_session.get(
            url=f"{base}/wrong-path",
            timeout=self.api_comment.timeout
        )
        assert response.status_code == 404, response.text
        assert response.json().get("error") == "PATH_NOT_FOUND"
