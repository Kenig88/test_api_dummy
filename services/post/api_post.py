import allure
import requests
from typing import Optional

from services.api_base import ApiBase
from utils.helper import Helper
from services.post.post_endpoints import PostEndpoints
from services.post.post_payload import PostPayload
from services.post.post_models import PostResponseModel, PostListResponseModel, PostDeleteResponseModel


class ApiPost(ApiBase, Helper):
    def __init__(self, http_session: requests.Session, endpoints: PostEndpoints, timeout: int = 15):
        super().__init__(http_session=http_session, timeout=timeout)
        self.endpoint = endpoints

    # ----------------------------------------------------- CRUD -------------------------------------------------------
    # CRUD = Create, Read, Update, Delete (создать, прочитать, обновить, удалить), включая вызовы списков.

    @allure.step("POST == /post/create")
    def create_post(self, user_id: str, payload: dict | None = None) -> PostResponseModel:

        # 1) Если тест не передал payload, беру "шаблонный" payload
        if payload is None:
            payload = PostPayload.create_post_payload(user_id)

        # 2) Отправляю запрос POST на эндпоинт создания поста
        response = self.http_session.post(
            url=self.endpoint.create_post(),
            json=payload,
            timeout=self.timeout
        )

        # 3) Прикладываю response в Allure (чтобы в отчёте видеть запрос/ответ)
        self.attach_response_safe(response)

        # 4) Проверяю статус-код:
        #    часто create возвращает 200 или 201 (created)
        body = self._check_status_code(response, ok_statuses=[200, 201])

        # 5) Валидирую и превращаем dict в PostResponseModel (Pydantic v2)
        return PostResponseModel.model_validate(body)

    @allure.step("GET == /user/{user_id}/post")
    def get_list_posts_by_user_id(self, user_id: str, page: int, limit: int) -> list[PostListResponseModel]:

        # 1) Отправляю GET запрос с query-параметрами page/limit
        response = self.http_session.get(
            url=self.endpoint.get_list_posts_by_user_id(user_id),
            params={"page": page, "limit": limit},
            timeout=self.timeout
        )

        # 2) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 3) Проверяю, что сервер вернул 200
        body = self._check_status_code(response, ok_statuses=[200])

        # 4) Обычно список лежит в поле "data":
        posts_data = body.get("data", [])

        # 5) Каждый элемент списка превращаю в PostListResponseModel
        return [PostListResponseModel.model_validate(posts) for posts in posts_data]

    @allure.step("GET == /post?page=*&limit=*")
    def get_list_posts(self, page: int, limit: int) -> list[PostListResponseModel]:

        # 1) Отправляю GET запрос с query-параметрами page/limit
        response = self.http_session.get(
            url=self.endpoint.get_list_posts(),
            params={"page": page, "limit": limit},
            timeout=self.timeout
        )

        # 2) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 3) Проверяю, что сервер вернул 200
        body = self._check_status_code(response, ok_statuses=[200])

        # 4) Обычно список лежит в поле "data":
        posts_data = body.get("data", [])

        # 5) Каждый элемент списка превращаю в PostsListResponseModel
        return [PostListResponseModel.model_validate(posts) for posts in posts_data]

    @allure.step("GET == /post/{post_id}")
    def get_post_by_id(self, post_id: str) -> PostResponseModel:

        # 1) Отправляю GET запрос на /post/{post_id}
        response = self.http_session.get(
            url=self.endpoint.get_post_by_post_id(post_id),
            timeout=self.timeout
        )

        # 2) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 3) Ожидаю статус 200 (успешно)
        body = self._check_status_code(response, ok_statuses=[200])

        # 4) Превращаю JSON в модель
        return PostResponseModel.model_validate(body)

    @allure.step("PUT == /post/{post_id}")
    def update_post(self, post_id: str, payload: dict | None = None) -> PostResponseModel:

        # 1) Если тест не передал payload, беру "шаблонный" payload
        if payload is None:
            payload = PostPayload.update_post_payload()

        # 2) Отправляю PUT запрос на /post/{post_id} с JSON телом
        response = self.http_session.put(
            url=self.endpoint.update_post(post_id),
            json=payload,
            timeout=self.timeout
        )

        # 3) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 4) Проверяю статус 200
        body = self._check_status_code(response, ok_statuses=[200])

        # 5) Возвращаю обновлённую модель
        return PostResponseModel.model_validate(body)

    @allure.step("DELETE == /post/{post_id}")
    def delete_post(self, post_id: str, allow_not_found: bool = False) -> Optional[PostDeleteResponseModel]:

        # 1) Отправляю DELETE запрос на /post/{post_id}
        response = self.http_session.delete(
            url=self.endpoint.delete_post(post_id),
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
        return PostDeleteResponseModel.model_validate(body) if body else None
