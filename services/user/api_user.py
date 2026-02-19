from typing import Optional

from services.user.user_models import UserResponseModel, UserListResponseModel, UserDeleteResponseModel
from utils.helper import Helper
import allure
import requests
from services.user.user_endpoints import UserEndpoints
from services.user.user_payloads import UserPayloads


class ApiUser(Helper):
    def __init__(self, http_session: requests.Session, endpoints: UserEndpoints, timeout: int = 15):
        self.http_session = http_session
        self.endpoint = endpoints
        self.timeout = timeout

    def _json(self, response: requests.Response) -> dict:
        try:
            return response.json()
        except ValueError:
            return {"text": response.text}

    def _check_status_code(self, response: requests.Response, ok_statuses: list[int]) -> dict:
        body = self._json(response)
        assert response.status_code in ok_statuses, body
        return body

    # ----------------------------------------------------- CRUD -------------------------------------------------------
    # CRUD = Create, Read, Update, Delete (создать, прочитать, обновить, удалить), включая вызовы списков.

    @allure.step("POST == /user/create")
    def create_user(self, payload: dict | None = None) -> UserResponseModel:

        # 1) Если тест не передал payload, берём "шаблонный" payload
        if payload is None:
            payload = UserPayloads.create_user_payload()

        # 2) Отправляем запрос POST на эндпоинт создания пользователя
        response = self.http_session.post(
            url=self.endpoint.create_user(),
            json=payload,
            timeout=self.timeout
        )

        # 3) Прикладываем response в Allure (чтобы в отчёте видеть запрос/ответ)
        self.attach_response_safe(response)

        # 4) Проверяем статус-код:
        #    часто create возвращает 200 или 201 (created)
        body = self._check_status_code(response, ok_statuses=[200, 201])

        # 5) Валидируем и превращаем dict в UserCreateModel (Pydantic v2)
        return UserResponseModel.model_validate(body)

    @allure.step("GET == /user")
    def get_list_users(self, page: int, limit: int) -> list[UserListResponseModel]:

        # 1) Отправляем GET запрос на /user с query-параметрами limit/page
        response = self.http_session.get(
            url=self.endpoint.get_list_users(),
            params={"page": page, "limit": limit},
            timeout=self.timeout
        )

        # 2) Прикладываем ответ в Allure
        self.attach_response_safe(response)

        # 3) Проверяем, что сервер вернул 200
        body = self._check_status_code(response, ok_statuses=[200])

        # 4) Обычно список лежит в поле "data":
        users_data = body.get("data", [])

        # 5) Каждый элемент списка превращаем в UserResponseModel
        return [UserListResponseModel.model_validate(users) for users in users_data]

    @allure.step("GET == /user/:id")
    def get_user_by_id(self, user_id: str) -> UserResponseModel:

        # 1) Отправляем GET запрос на /user/{user_id}
        response = self.http_session.get(
            url=self.endpoint.get_user_by_id(user_id),
            timeout=self.timeout
        )

        # 2) Прикладываем ответ в Allure
        self.attach_response_safe(response)

        # 3) Ожидаем статус 200 (успешно)
        body = self._check_status_code(response, ok_statuses=[200])

        # 4) Превращаем JSON в модель
        return UserResponseModel.model_validate(body)

    @allure.step("PUT == /user/:id")
    def update_user(self, user_id: str, payload: dict | None = None) -> UserResponseModel:

        # 1) Если тест не передал payload, берём "шаблонный" payload
        if payload is None:
            payload = UserPayloads.create_user_payload()

        # 2) Отправляем PUT запрос на /user/{user_id} с JSON телом
        response = self.http_session.put(
            url=self.endpoint.update_user(user_id),
            json=payload,
            timeout=self.timeout
        )

        # 3) Прикладываем ответ в Allure
        self.attach_response_safe(response)

        # 4) Проверяем статус 200
        body = self._check_status_code(response, ok_statuses=[200])

        # 5) Возвращаем обновлённую модель
        return UserResponseModel.model_validate(body)

    @allure.step("DELETE == /user/:id")
    def delete_user(self, user_id: str, allow_not_found: bool = False) -> Optional[UserDeleteResponseModel]:

        # 1) Отправляем DELETE запрос на /user/{user_id}
        response = self.http_session.delete(
            url=self.endpoint.delete_user(user_id),
            timeout=self.timeout
        )

        # 2) Прикладываем ответ в Allure
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
