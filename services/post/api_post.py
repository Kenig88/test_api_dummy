import allure
import requests

from services.api_base import ApiBase
from services.error_models import ErrorResponseModel
from services.post.post_endpoints import PostEndpoints
from services.post.post_models import (
    PostDeleteResponseModel,
    PostListResponseModel,
    PostResponseModel,
)
from services.post.post_payload import PostPayload


class ApiPost(ApiBase):
    def __init__(self, http_session: requests.Session, endpoints: PostEndpoints, timeout: int = 15):
        super().__init__(http_session=http_session, timeout=timeout)
        self.endpoint = endpoints

    @allure.step("POST == /post/create")
    def create_post(self, user_id: str, payload: dict | None = None) -> PostResponseModel:
        if payload is None:
            payload = PostPayload.create_post_payload(user_id)
        else:
            payload = dict(payload)
            if payload.get("owner") != user_id:
                raise ValueError("payload['owner'] must match user_id")

        response = self.send_request(
            method="POST",
            url=self.endpoint.create_post(),
            json=payload,
        )
        body = self._check_status_code(response, ok_statuses=[200, 201])
        return PostResponseModel.model_validate(body)

    @allure.step("GET == /user/{user_id}/post")
    def get_list_posts_by_user_id(self, user_id: str, page: int, limit: int) -> PostListResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_posts_by_user_id(user_id),
            params={"page": page, "limit": limit},
        )
        body = self._check_status_code(response, ok_statuses=[200])
        return PostListResponseModel.model_validate(body)

    @allure.step("GET == /post?page=*&limit=*")
    def get_list_posts(self, page: int, limit: int) -> PostListResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_posts(),
            params={"page": page, "limit": limit},
        )
        body = self._check_status_code(response, ok_statuses=[200])
        return PostListResponseModel.model_validate(body)

    @allure.step("GET == /post/{post_id}")
    def get_post_by_id(
        self,
        post_id: str,
        expected_status_code: int = 200,
    ) -> PostResponseModel | ErrorResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_post_by_post_id(post_id),
        )
        body = self._check_status_code(response, ok_statuses=[expected_status_code])

        if expected_status_code == 200:
            return PostResponseModel.model_validate(body)

        return ErrorResponseModel.model_validate(body)

    @allure.step("PUT == /post/{post_id}")
    def update_post(self, post_id: str, payload: dict | None = None) -> PostResponseModel:
        if payload is None:
            payload = PostPayload.update_post_payload()

        response = self.send_request(
            method="PUT",
            url=self.endpoint.update_post(post_id),
            json=payload,
        )
        body = self._check_status_code(response, ok_statuses=[200])
        return PostResponseModel.model_validate(body)

    @allure.step("DELETE == /post/{post_id}")
    def delete_post(
        self,
        post_id: str,
        expected_status_code: int = 200,
        allow_not_found: bool = False,
    ) -> PostDeleteResponseModel | ErrorResponseModel | None:
        response = self.send_request(
            method="DELETE",
            url=self.endpoint.delete_post(post_id),
        )

        if allow_not_found and response.status_code == 404:
            return None

        body = self._check_status_code(response, ok_statuses=[expected_status_code])

        if expected_status_code == 204:
            return None
        if expected_status_code == 200:
            return PostDeleteResponseModel.model_validate(body)
        return ErrorResponseModel.model_validate(body)
