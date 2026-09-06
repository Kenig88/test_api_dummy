import logging
import os
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from services.comment.api_comment import ApiComment
from services.comment.comment_endpoints import CommentEndpoints
from services.comment.comment_payload import CommentPayload
from services.post.api_post import ApiPost
from services.post.post_endpoints import PostEndpoints
from services.post.post_payloads import PostPayloads
from services.user.api_user import ApiUser
from services.user.user_endpoints import UserEndpoints
from services.user.user_payloads import UserPayloads

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
LOGS_DIR = PROJECT_ROOT / "logs"
DEFAULT_TIMEOUT = 15
SAFE_METHOD_RETRIES = 1

logger = logging.getLogger("tests")


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    LOGS_DIR.mkdir(exist_ok=True)

    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
    config.option.log_file = str(LOGS_DIR / f"api-tests-{worker}.log")

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("faker").setLevel(logging.WARNING)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.failed:
        item._test_outcome = "FAILED" if report.when == "call" else "ERROR"
    elif report.skipped and not hasattr(item, "_test_outcome"):
        item._test_outcome = "SKIPPED"
    elif report.when == "call":
        item._test_outcome = "PASSED"

    if report.when == "teardown":
        worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
        result = getattr(item, "_test_outcome", "FINISHED")
        logger.info("[%s] END TEST: %s -> %s", worker, item.nodeid, result)


@pytest.fixture(autouse=True)
def log_test_start(request):
    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
    test_name = request.node.nodeid

    logger.info("[%s] START TEST: %s", worker, test_name)
    yield


def _get_env(name: str) -> str:
    value = os.getenv(name)
    assert value, f"Переменная {name} не задана в окружении или .env"
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
    retry = Retry(
        total=SAFE_METHOD_RETRIES,
        connect=SAFE_METHOD_RETRIES,
        read=SAFE_METHOD_RETRIES,
        status=SAFE_METHOD_RETRIES,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(
        {
            "app-id": api_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )
    yield session
    session.close()


# ======================================================== USER ========================================================


@pytest.fixture(scope="session")
def user_endpoints(base_url: str) -> UserEndpoints:
    return UserEndpoints(base_url)


@pytest.fixture(scope="session")
def api_user(http_session: requests.Session, user_endpoints: UserEndpoints) -> ApiUser:
    return ApiUser(http_session=http_session, endpoints=user_endpoints, timeout=DEFAULT_TIMEOUT)


@pytest.fixture
def created_user(api_user: ApiUser):
    created_user_ids: list[str] = []

    def create_user(overrides: dict | None = None):
        payload = UserPayloads.create_user_payload()
        if overrides:
            payload.update(overrides)

        user = api_user.create_user(payload)
        created_user_ids.append(str(user.id))
        return user

    yield create_user

    for user_id in created_user_ids:
        api_user.delete_user(user_id, allow_not_found=True)


# ======================================================== POST ========================================================


@pytest.fixture(scope="session")
def post_endpoints(base_url: str) -> PostEndpoints:
    return PostEndpoints(base_url)


@pytest.fixture(scope="session")
def api_post(http_session: requests.Session, post_endpoints: PostEndpoints) -> ApiPost:
    return ApiPost(http_session=http_session, endpoints=post_endpoints, timeout=DEFAULT_TIMEOUT)


@pytest.fixture
def created_post(api_post: ApiPost, created_user):
    created_post_ids: list[str] = []

    def create_post(user_id: str | None = None, overrides: dict | None = None):
        if user_id is None:
            user_id = str(created_user().id)

        payload = PostPayloads.create_post_payload(user_id)
        if overrides:
            payload.update(overrides)

        post = api_post.create_post(user_id=user_id, payload=payload)
        created_post_ids.append(str(post.id))
        return post

    yield create_post

    for post_id in created_post_ids:
        api_post.delete_post(post_id, allow_not_found=True)


# ====================================================== COMMENT =======================================================


@pytest.fixture(scope="session")
def comment_endpoints(base_url: str) -> CommentEndpoints:
    return CommentEndpoints(base_url)


@pytest.fixture(scope="session")
def api_comment(http_session: requests.Session, comment_endpoints: CommentEndpoints) -> ApiComment:
    return ApiComment(http_session=http_session, endpoints=comment_endpoints, timeout=DEFAULT_TIMEOUT)


@pytest.fixture
def created_comment(api_comment: ApiComment, created_user, created_post):
    created_comment_ids: list[str] = []

    def create_comment(user_id: str | None = None, post_id: str | None = None, overrides: dict | None = None):
        if user_id is None:
            user_id = str(created_user().id)
        if post_id is None:
            post_id = str(created_post(user_id=user_id).id)

        payload = CommentPayload.comment_create_payload(user_id, post_id)
        if overrides:
            payload.update(overrides)

        comment = api_comment.create_comment(user_id=user_id, post_id=post_id, payload=payload)
        created_comment_ids.append(str(comment.id))
        return comment

    yield create_comment

    for comment_id in created_comment_ids:
        api_comment.delete_comment(comment_id, allow_not_found=True)
