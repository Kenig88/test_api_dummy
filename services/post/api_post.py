import allure
import requests
from typing import Optional
from utils.helper import Helper
from services.post.post_endpoints import PostEndpoints
from services.post.post_payload import PostPayload
from services.post.post_models import PostResponseModel, PostListResponseModel, PostDeleteResponseModel

from services.api_base import ApiBase


class ApiPost(Helper):
    def __init__(self, http_session: requests.Session, endpoints: PostEndpoints, timeout: int = 15):
        self.http_session = http_session,
        self.endpoint = endpoints
        self.timeout = timeout

    # ----------------------------------------------------- CRUD -------------------------------------------------------
    # CRUD = Create, Read, Update, Delete (создать, прочитать, обновить, удалить), включая вызовы списков.

    @allure.step("POST == /post/create")
    def create_post(self, user_id: str, payload: dict | None = None) -> PostResponseModel:
        pass

    @allure.step("GET == /user/{user_id}/post")
    def get_posts_list_by_user_id(self, user_id: str, page: int, limit: int) -> PostListResponseModel:
        pass

    @allure.step("GET == /post?page=*&limit=*")
    def get_list_posts(self, page: int, limit: int) -> PostListResponseModel:
        pass

    @allure.step("GET == /post/{post_id}")
    def get_post_by_id(self, post_id: str) -> PostResponseModel:
        pass

    @allure.step("PUT == /post/{post_id}")
    def update_post(self, post_id: str, payload: dict | None = None) -> PostResponseModel:
        pass

    @allure.step("DELETE == /post/{post_id}")
    def delete_post(self, post_id: str) -> Optional[PostDeleteResponseModel]:
        pass
