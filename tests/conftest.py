import os
import pytest
import requests
from dotenv import load_dotenv

from services.user.user_endpoints import UserEndpoints
from services.user.user_payloads import UserPayloads
from services.user.api_user import ApiUser

load_dotenv()
DEFAULT_TIMEOUT: int = 15


def _get_env(name: str) -> str:
    """Беру переменную из окружения и если её нет - падает с понятной ошибкой"""
    value = os.getenv(name)
    assert value, f" Переменная {name} не задана в .env"
    return value


@pytest.fixture(scope="session")
def base_url() -> str:
    return _get_env("BASE_URL")


@pytest.fixture(scope="session")
def api_token() -> str:
    return _get_env("API_TOKEN")


@pytest.fixture(scope="session")
def http_session(api_token: str) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "app-id": api_token,
            "Accept": "application/json",  # проверь в документации нужно ли
            "Content-Type": "application/json"  # проверь в документации нужно ли
        }
    )
    yield session
    session.close()


# ========================================================USER==========================================================
# ======================================================================================================================
# ========================================================USER==========================================================

@pytest.fixture(scope="session")
def user_endpoints(base_url: str) -> UserEndpoints:
    return UserEndpoints(base_url)


@pytest.fixture(scope="session")
def api_user(http_session: requests.Session, user_endpoints: UserEndpoints) -> ApiUser:
    return ApiUser(http_session=http_session, endpoints=user_endpoints, timeout=DEFAULT_TIMEOUT)


@pytest.fixture(scope="session")
def created_user(api_user: ApiUser):
    created_ids: list[str] = []

    def create_user():
        # 1) генерирую базовый payload
        payload = UserPayloads.create_user_payload()


        # !!!этот шаг не вставлял!! так же **overrides в параметр create_user()!!!
        # 2) применяю переопределения (например name="Alex")
        # payload.update(overrides)


        # 3) создаю пользователя
        user = api_user.create_user(payload)

        # 4) сохраняю id, чтобы потом удалить
        created_ids.append(str(user.id))

        return user  # возвращаем модель пользователя

    yield create_user

    # cleanup: удаляю всех созданных пользователей
    for uid in created_ids:
        api_user.delete_user(uid, allow_not_found=True)

# ========================================================POST==========================================================
# ======================================================================================================================
# ========================================================POST==========================================================


# ======================================================COMMENT=========================================================
# ======================================================================================================================
# ======================================================COMMENT=========================================================
