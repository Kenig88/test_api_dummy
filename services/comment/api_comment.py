import allure
import requests

from services.api_base import ApiBase
from services.comment.comment_endpoints import CommentEndpoints
from services.comment.comment_models import (
    CommentDeleteResponseModel,
    CommentResponseModel,
    CommentsListResponseModel,
)
from services.comment.comment_payload import CommentPayload
from services.error_models import ErrorResponseModel


class ApiComment(ApiBase):
    def __init__(self, http_session: requests.Session, endpoints: CommentEndpoints, timeout: int = 15):
        super().__init__(http_session=http_session, timeout=timeout)
        self.endpoint = endpoints

    @allure.step("POST == /comment/create")
    def create_comment(self, user_id: str, post_id: str, payload: dict | None = None) -> CommentResponseModel:
        if payload is None:
            payload = CommentPayload.comment_create_payload(user_id, post_id)
        else:
            payload = dict(payload)
            if payload.get("owner") != user_id:
                raise ValueError("payload['owner'] must match user_id")
            if payload.get("post") != post_id:
                raise ValueError("payload['post'] must match post_id")

        response = self.send_request(
            method="POST",
            url=self.endpoint.create_comment(),
            json=payload,
        )
        body = self._check_status_code(response, ok_statuses=[200, 201])
        return CommentResponseModel.model_validate(body)

    @allure.step("GET == /user/{user_id}/comment")
    def get_list_comments_by_user_id(self, user_id: str, page: int, limit: int) -> CommentsListResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_comments_by_user_id(user_id),
            params={"page": page, "limit": limit},
        )
        body = self._check_status_code(response, ok_statuses=[200])
        return CommentsListResponseModel.model_validate(body)

    @allure.step("GET == /post/{post_id}/comment")
    def get_list_comments_by_post_id(self, post_id: str, page: int, limit: int) -> CommentsListResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_comments_by_post_id(post_id),
            params={"page": page, "limit": limit},
        )
        body = self._check_status_code(response, ok_statuses=[200])
        return CommentsListResponseModel.model_validate(body)

    @allure.step("GET == /comment?page=*&limit=*")
    def get_list_comments(
        self,
        page: int,
        limit: int,
        created_only: bool = False,
    ) -> CommentsListResponseModel:
        params = {"page": page, "limit": limit}
        if created_only:
            # Публичная база DummyAPI может содержать старые некорректные записи.
            # created=1 оставляет только данные текущего app-id.
            params["created"] = 1

        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_comments(),
            params=params,
        )
        body = self._check_status_code(response, ok_statuses=[200])
        return CommentsListResponseModel.model_validate(body)

    @allure.step("DELETE == /comment/{comment_id}")
    def delete_comment(
        self,
        comment_id: str,
        expected_status_code: int = 200,
        allow_not_found: bool = False,
    ) -> CommentDeleteResponseModel | ErrorResponseModel | None:
        response = self.send_request(
            method="DELETE",
            url=self.endpoint.delete_comment(comment_id),
        )

        if allow_not_found and response.status_code == 404:
            return None

        body = self._check_status_code(response, ok_statuses=[expected_status_code])

        if expected_status_code == 204:
            return None
        if expected_status_code == 200:
            return CommentDeleteResponseModel.model_validate(body)
        return ErrorResponseModel.model_validate(body)
