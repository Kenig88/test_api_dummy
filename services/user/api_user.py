import allure
import requests
from typing import Optional

from services.api_base import ApiBase
from utils.helper import Helper
from services.user.user_endpoints import UserEndpoints
from services.user.user_payloads import UserPayloads
from services.user.user_models import UserResponseModel, UserListResponseModel, UserDeleteResponseModel


class ApiUser(ApiBase, Helper):
    def __init__(self, http_session: requests.Session, endpoints: UserEndpoints, timeout: int = 15):
        super().__init__(http_session=http_session, timeout=timeout)
        self.endpoint = endpoints

    # ----------------------------------------------------- CRUD -------------------------------------------------------
    # CRUD = Create, Read, Update, Delete (создать, прочитать, обновить, удалить), включая вызовы списков.

    @allure.step("POST == /user/create")
    def create_user(self, payload: dict | None = None) -> UserResponseModel:

        # 1) Если тест не передал payload, беру "шаблонный" payload
        if payload is None:
            payload = UserPayloads.create_user_payload()

        # 2) Отправляю запрос POST на эндпоинт создания пользователя
        response = self.http_session.post(
            url=self.endpoint.create_user(),
            json=payload,
            timeout=self.timeout
        )

        # 3) Прикладываю response в Allure (чтобы в отчёте видеть запрос/ответ)
        self.attach_response_safe(response)

        # 4) Проверяем статус-код:
        #    часто create возвращает 200 или 201 (created)
        body = self._check_status_code(response, ok_statuses=[200, 201])

        # 5) Валидирую и превращаем dict в UserCreateModel (Pydantic v2)
        return UserResponseModel.model_validate(body)

    @allure.step("GET == /user?page=*&limit=*")
    def get_list_users(self, page: int, limit: int) -> list[UserListResponseModel]:

        # 1) Отправляю GET запрос с query-параметрами limit/page
        response = self.http_session.get(
            url=self.endpoint.get_list_users(),
            params={"page": page, "limit": limit},
            timeout=self.timeout
        )

        # 2) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 3) Проверяю, что сервер вернул 200
        body = self._check_status_code(response, ok_statuses=[200])

        # 4) Обычно список лежит в поле "data":
        users_data = body.get("data", [])

        # 5) Каждый элемент списка превращаю в UserListResponseModel
        return [UserListResponseModel.model_validate(users) for users in users_data]

    @allure.step("GET == /user/{user_id}")
    def get_user_by_id(self, user_id: str) -> UserResponseModel:

        # 1) Отправляю GET запрос на /user/{user_id}
        response = self.http_session.get(
            url=self.endpoint.get_user_by_id(user_id),
            timeout=self.timeout
        )

        # 2) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 3) Ожидаю статус 200 (успешно)
        body = self._check_status_code(response, ok_statuses=[200])

        # 4) Превращаю JSON в модель
        return UserResponseModel.model_validate(body)

    @allure.step("PUT == /user/{user_id}")
    def update_user(self, user_id: str, payload: dict | None = None) -> UserResponseModel:

        # 1) Если тест не передал payload, беру "шаблонный" payload
        if payload is None:
            payload = UserPayloads.create_user_payload()

        # 2) Отправляю PUT запрос на /user/{user_id} с JSON телом
        response = self.http_session.put(
            url=self.endpoint.update_user(user_id),
            json=payload,
            timeout=self.timeout
        )

        # 3) Прикладываю ответ в Allure
        self.attach_response_safe(response)

        # 4) Проверяю статус 200
        body = self._check_status_code(response, ok_statuses=[200])

        # 5) Возвращаю обновлённую модель
        return UserResponseModel.model_validate(body)

    @allure.step("DELETE == /user/{user_id}")
    def delete_user(self, user_id: str, allow_not_found: bool = False) -> Optional[UserDeleteResponseModel]:

        # 1) Отправляю DELETE запрос на /user/{user_id}
        response = self.http_session.delete(
            url=self.endpoint.delete_user(user_id),
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
        return UserDeleteResponseModel.model_validate(body) if body else None
