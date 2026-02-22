import os
import pytest
import requests
from dotenv import load_dotenv

from services.user.user_endpoints import UserEndpoints
from services.user.user_payloads import UserPayloads
from services.user.api_user import ApiUser

from services.post.post_endpoints import PostEndpoints
from services.post.post_payload import PostPayload
from services.post.api_post import ApiPost

from services.comment.comment_endpoints import CommentEndpoints
from services.comment.comment_payload import CommentPayload
from services.comment.api_comment import ApiComment

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
    created_user_ids: list[str] = []

    def create_user(overrides: dict | None = None):

        # 1) генерирую базовый payload
        payload = UserPayloads.create_user_payload()
        if overrides:
            payload.update(overrides)

        # 3) создаю пользователя
        user = api_user.create_user(payload)

        # 4) сохраняю id, чтобы потом удалить
        created_user_ids.append(str(user.id))
        return user  # возвращаем модель пользователя

    yield create_user

    # cleanup: удаляю всех созданных пользователей
    for uid in created_user_ids:
        api_user.delete_user(uid, allow_not_found=True)


# ========================================================POST==========================================================
# ======================================================================================================================
# ========================================================POST==========================================================

@pytest.fixture(scope="session")
def post_endpoints(base_url: str) -> PostEndpoints:
    return PostEndpoints(base_url)


@pytest.fixture(scope="session")
def api_post(http_session: requests.Session, post_endpoints: PostEndpoints) -> ApiPost:
    return ApiPost(http_session=http_session, endpoints=post_endpoints, timeout=DEFAULT_TIMEOUT)


@pytest.fixture(scope="session")
def created_post(api_post: ApiPost, created_user):
    created_post_ids: list[str] = []

    def create_post(user_id: str | None = None, overrides: dict | None = None):
        # если владелец не задан — создаём нового пользователя
        if user_id is None:
            user = created_user()
            user_id = str(user.id)

        payload = PostPayload.create_post_payload(user_id)
        if overrides:
            payload.update(overrides)

        post = api_post.create_post(user_id=user_id, payload=payload)

        created_post_ids.append(str(post.id))
        return post

    yield create_post

    for pid in created_post_ids:
        api_post.delete_post(pid, allow_not_found=True)


# ======================================================COMMENT=========================================================
# ======================================================================================================================
# ======================================================COMMENT=========================================================

@pytest.fixture(scope="session")
def comment_endpoints(base_url: str) -> CommentEndpoints:
    return CommentEndpoints(base_url)


@pytest.fixture(scope="session")
def api_comment(http_session: requests.Session, comment_endpoints: CommentEndpoints) -> ApiComment:
    return ApiComment(http_session=http_session, endpoints=comment_endpoints, timeout=DEFAULT_TIMEOUT)


@pytest.fixture(scope="session")
def created_comment(api_comment: ApiComment, created_user, created_post):
    created_comment_ids: list[str] = []

    def create_comment(user_id: str | None = None, post_id: str | None = None):
        if user_id is None:
            user_id = str(created_user().id)
        if post_id is None:
            post_id = str(created_post().id)

        payload = CommentPayload.comment_create_payload(user_id, post_id)
        comment = api_comment.create_comment(payload)

        created_comment_ids.append(str(comment.id))
        return comment

    yield create_comment

    for cid in created_comment_ids:
        api_comment.delete_comment(cid, allow_not_found=True)
