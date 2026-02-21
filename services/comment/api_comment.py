import allure
import requests
from typing import Optional

from services.api_base import ApiBase
from utils.helper import Helper
from services.comment.comment_endpoints import CommentEndpoints
from services.comment.comment_payload import CommentPayload
from services.comment.comment_models import CommentResponseModel, CommentsListResponseModel, CommentDeleteResponseModel


class ApiComment(ApiBase, Helper):
    def __init__(self, http_session: requests.Session, endpoints: CommentEndpoints, timeout: int = 15):
        super().__init__(self, http_session=http_session, timeout=timeout)
        self.endpoint = endpoints

    # ----------------------------------------------------- CRUD -------------------------------------------------------
    # CRUD = Create, Read, Update, Delete (создать, прочитать, обновить, удалить), включая вызовы списков.

    @allure.step("CREATE == /comment/create")
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
    def get_list_comments_by_user_id(self, user_id: str, page: int, limit: int) -> list[CommentsListResponseModel]:

        # 1) Отправляю GET запрос с query-параметрами page/limit
        response = self.http_session.get(
            url=self.endpoint.get_list_comments_by_user_id(user_id),
            params={"page": page, "limit": limit},
            timeout=self.timeout
        )

        # 2) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 3) Проверяю, что сервер вернул 200
        body = self._check_status_code(response, ok_statuses=[200])

        # 4) Обычно список лежит в поле "data":
        comments_data = body.get("comments", [])

        # 5) Каждый элемент списка превращаю в CommentsListResponseModel
        return [CommentsListResponseModel.model_validate(comments for comments in comments_data)]

    @allure.step("GET == /post/{post_id}/comment")
    def get_clist_comments_by_post_id(self, post_id: str, page: int, limit: int) -> list[CommentsListResponseModel]:

        # 1) Отправляю GET запрос с query-параметрами page/limit
        response = self.http_session.get(
            url=self.endpoint.get_list_comments_by_post_id(post_id),
            params={"page": page, "limit": limit},
            timeout=self.timeout
        )

        # 2) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 3) Проверяю, что сервер вернул 200
        body = self._check_status_code(response, ok_statuses=[200])

        # 4) Обычно список лежит в поле "data":
        comments_data = body.get("comments", [])

        # 5) Каждый элемент списка превращаю в CommentsListResponseModel
        return [CommentsListResponseModel.model_validate(comments) for comments in comments_data]

    @allure.step("GET == /comment?page=*&limit=*")
    def get_list_comments(self, page: int, limit: int) -> list[CommentsListResponseModel]:

        # 1) Отправляю GET запрос с query-параметрами page/limit
        response = self.http_session.get(
            url=self.endpoint.get_list_comments(),
            params={"page": page, "limit": limit},
            timeout=self.timeout
        )

        # 2) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 3) Проверяю, что сервер вернул 200
        body = self._check_status_code(response, ok_statuses=[200])

        # 4) Обычно список лежит в поле "data":
        comments_data = body.get("data", [])

        # 5) Каждый элемент списка превращаю в CommentsListResponseModel
        return [CommentsListResponseModel.model_validate(comments) for comments in comments_data]

    @allure.step("DELETE == /comment/{comment_id}")
    def delete_comment(self, comment_id: str, allow_not_found: bool = False) -> Optional[CommentDeleteResponseModel]:

        # 1) Отправляю DELETE запрос на /comment/{comment_id}
        response = self.http_session.delete(
            url=self.endpoint.delete_comment(comment_id),
            timeout=self.timeout
        )

        # 2) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 3.1) Если "не найдено" и сервер вернул 404 или cleanup в фикстуре
        if allow_not_found and response.status_code == 404:
            return None

        # Разрешаю только "успешные" коды
        self._check_status_code(response, ok_statuses=[200, 204])

        # 3.2) Если тела нет = 204
        if response.status_code == 204:
            return None

        # 4) # 200 с JSON-телом
        body = self._json(response)
        return CommentDeleteResponseModel.model_validate(body) if body else None
