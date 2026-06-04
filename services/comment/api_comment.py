from typing import Optional

import allure
import requests

from services.api_base import ApiBase
from services.comment.comment_endpoints import CommentEndpoints
from services.comment.comment_models import (
    CommentAfterDeleteResponseModel,
    CommentDeleteResponseModel,
    CommentResponseModel,
    CommentsListResponseModel,
)
from services.comment.comment_payload import CommentPayload


class ApiComment(ApiBase):
    def __init__(self, http_session: requests.Session, endpoints: CommentEndpoints, timeout: int = 15):
        super().__init__(http_session=http_session, timeout=timeout)
        self.endpoint = endpoints

    @allure.step("POST == /comment/create")
    def create_comment(self, user_id: str, post_id: str, payload: dict | None = None) -> CommentResponseModel:
        if payload is None:
            payload = CommentPayload.comment_create_payload(user_id, post_id)

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
    def get_list_comments(self, page: int, limit: int) -> CommentsListResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_comments(),
            params={"page": page, "limit": limit},
        )
        body = self._check_status_code(response, ok_statuses=[200])
        return CommentsListResponseModel.model_validate(body)

    @allure.step("DELETE == /comment/{comment_id}")
    def delete_comment(
        self,
        comment_id: str,
        allow_not_found: bool = False,
    ) -> Optional[CommentDeleteResponseModel | CommentAfterDeleteResponseModel]:
        response = self.send_request(
            method="DELETE",
            url=self.endpoint.delete_comment(comment_id),
        )

        if allow_not_found and response.status_code == 404:
            return None

        body = self._check_status_code(response, ok_statuses=[200, 404])
        if response.status_code == 200:
            return CommentDeleteResponseModel.model_validate(body)
        if response.status_code == 404:
            return CommentAfterDeleteResponseModel.model_validate(body)

        return None
