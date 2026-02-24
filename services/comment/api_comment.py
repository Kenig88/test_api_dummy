import allure
import requests
from typing import Optional

from services.api_base import ApiBase
from utils.helper import Helper
from services.comment.comment_endpoints import CommentEndpoints
from services.comment.comment_payload import CommentPayload
from services.comment.comment_models import (CommentResponseModel, CommentsListResponseModel, \
                                             CommentDeleteResponseModel, CommentAfterDeleteResponseModel)


class ApiComment(ApiBase, Helper):
    def __init__(self, http_session: requests.Session, endpoints: CommentEndpoints, timeout: int = 15):
        super().__init__(http_session=http_session, timeout=timeout)
        self.endpoint = endpoints

    # ----------------------------------------------------- CRUD -------------------------------------------------------
    # CRUD = Create, Read, Update, Delete (создать, прочитать, обновить, удалить), включая вызовы списков.

    @allure.step("POST == /comment/create")
    def create_comment(self, user_id: str, post_id: str, payload: dict | None = None) -> CommentResponseModel:

        # 1) Если тест не передал payload, беру "шаблонный" payload
        if payload is None:
            payload = CommentPayload.comment_create_payload(user_id, post_id)

        # 2) Отправляю запрос POST на эндпоинт создания коммента
        response = self.http_session.post(
            url=self.endpoint.create_comment(),
            json=payload,
            timeout=self.timeout
        )

        # 3) Прикладываю response в Allure (чтобы в отчёте видеть запрос/ответ)
        self.attach_response_safe(response)

        # 4) Проверяю статус-код:
        #    часто create возвращает 200 или 201 (created)
        body = self._check_status_code(response, ok_statuses=[200, 201])

        # 5) Валидирую и превращаем dict в PostResponseModel (Pydantic v2)
        return CommentResponseModel.model_validate(body)

    @allure.step("GET == /user/{user_id}/comment")
    def get_list_comments_by_user_id(self, user_id: str, page: int, limit: int) -> CommentsListResponseModel:

        # 1) Отправляю GET запрос с query-параметрами page/limit
        response = self.http_session.get(
            url=self.endpoint.get_list_comments_by_user_id(user_id),
            params={"page": page, "limit": limit},
            timeout=self.timeout
        )

        # 2) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 3) Проверяю, что сервер вернул 200 и забираю JSON body
        body = self._check_status_code(response, ok_statuses=[200])

        # 4) Валидирую ответ как пагинированный список (data + total/page/limit)
        return CommentsListResponseModel.model_validate(body)

    @allure.step("GET == /post/{post_id}/comment")
    def get_list_comments_by_post_id(self, post_id: str, page: int, limit: int) -> CommentsListResponseModel:

        # 1) Отправляю GET запрос с query-параметрами page/limit
        response = self.http_session.get(
            url=self.endpoint.get_list_comments_by_post_id(post_id),
            params={"page": page, "limit": limit},
            timeout=self.timeout
        )

        # 2) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 3) Проверяю, что сервер вернул 200 и забираю JSON body
        body = self._check_status_code(response, ok_statuses=[200])

        # 4) Валидирую ответ как пагинированный список (data + total/page/limit)
        return CommentsListResponseModel.model_validate(body)

    @allure.step("GET == /comment?page=*&limit=*")
    def get_list_comments(self, page: int, limit: int) -> CommentsListResponseModel:

        # 1) Отправляю GET запрос с query-параметрами page/limit
        response = self.http_session.get(
            url=self.endpoint.get_list_comments(),
            params={"page": page, "limit": limit},
            timeout=self.timeout
        )

        # 2) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 3) Проверяю, что сервер вернул 200 и забираю JSON body
        body = self._check_status_code(response, ok_statuses=[200])

        # 4) Валидирую ответ как пагинированный список (data + total/page/limit)
        return CommentsListResponseModel.model_validate(body)

    @allure.step("DELETE == /comment/{comment_id}")
    def delete_comment(self, comment_id: str):

        # 1) Отправляю DELETE запрос на /comment/{comment_id}
        response = self.http_session.delete(
            url=self.endpoint.delete_comment(comment_id),
            timeout=self.timeout
        )

        # 2) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 3) Допускаю только 200 (удалён) или 404 (не найден)
        body = self._check_status_code(response, ok_statuses=[200, 404])

        # 4) Если удаление прошло успешно (200) — валидирую как модель успешного удаления
        if response.status_code == 200:
            return CommentDeleteResponseModel.model_validate(body)

        # 5) Если не найдено (404) — валидирую как модель ошибки
        if response.status_code == 404:
            return CommentAfterDeleteResponseModel.model_validate(body)
