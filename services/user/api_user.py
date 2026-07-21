from typing import Optional

import allure
import requests

from services.api_base import ApiBase
from services.error_models import ErrorResponseModel
from services.user.user_endpoints import UserEndpoints
from services.user.user_models import (
    UserDeleteResponseModel,
    UserListResponseModel,
    UserResponseModel,
)
from services.user.user_payloads import UserPayloads


class ApiUser(ApiBase):
    def __init__(self, http_session: requests.Session, endpoints: UserEndpoints, timeout: int = 15):
        super().__init__(http_session=http_session, timeout=timeout)
        self.endpoint = endpoints

    @allure.step("POST == /user/create")
    def create_user(self, payload: dict | None = None) -> UserResponseModel:
        if payload is None:
            payload = UserPayloads.create_user_payload()

        response = self.send_request(
            method="POST",
            url=self.endpoint.create_user(),
            json=payload,
        )
        body = self._check_status_code(response, ok_statuses=[200, 201])
        return UserResponseModel.model_validate(body)

    @allure.step("GET == /user?page=*&limit=*")
    def get_list_users(self, page: int, limit: int) -> UserListResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_list_users(),
            params={"page": page, "limit": limit},
        )
        body = self._check_status_code(response, ok_statuses=[200])
        return UserListResponseModel.model_validate(body)

    @allure.step("GET == /user/{user_id}")
    def get_user_by_id(
        self,
        user_id: str,
        expected_status_code: int = 200,
    ) -> UserResponseModel | ErrorResponseModel:
        response = self.send_request(
            method="GET",
            url=self.endpoint.get_user_by_id(user_id),
        )
        body = self._check_status_code(response, ok_statuses=[expected_status_code])

        if expected_status_code == 200:
            return UserResponseModel.model_validate(body)

        return ErrorResponseModel.model_validate(body)

    @allure.step("PUT == /user/{user_id}")
    def update_user(self, user_id: str, payload: dict | None = None) -> UserResponseModel:
        if payload is None:
            payload = UserPayloads.update_user_payload()

        response = self.send_request(
            method="PUT",
            url=self.endpoint.update_user(user_id),
            json=payload,
        )
        body = self._check_status_code(response, ok_statuses=[200])
        return UserResponseModel.model_validate(body)

    @allure.step("DELETE == /user/{user_id}")
    def delete_user(
        self,
        user_id: str,
        expected_status_code: int = 200,
        allow_not_found: bool = False,
    ) -> Optional[UserDeleteResponseModel | ErrorResponseModel]:
        response = self.send_request(
            method="DELETE",
            url=self.endpoint.delete_user(user_id),
        )

        if allow_not_found and response.status_code == 404:
            return None

        if expected_status_code == 200:
            body = self._check_status_code(response, ok_statuses=[200, 204])
            if response.status_code == 204:
                return None
            return UserDeleteResponseModel.model_validate(body) if body else None

        body = self._check_status_code(response, ok_statuses=[expected_status_code])
        return ErrorResponseModel.model_validate(body)
