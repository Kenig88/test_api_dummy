from services.comment.comment_models import CommentResponseModel, CommentList, CommentDeleteResponseModel
from utils.helper import Helper
import requests
import allure

from services.api_base import ApiBase
from services.comment.comment_endpoints import CommentEndpoints


class ApiComment(Helper):
    def __init__(self, http_session: requests.Session, endpoints: CommentEndpoints, timeout: int = 15):
        self.http_session = http_session
        self.endpoint = endpoints
        self.timeout = timeout

    # ----------------------------------------------------- CRUD -------------------------------------------------------
    # CRUD = Create, Read, Update, Delete (создать, прочитать, обновить, удалить), включая вызовы списков.

    @allure.step("CREATE == /comment/create")
    def create_comment(self, user_id: str, post_id: str, payload: dict | None = None) -> CommentResponseModel:
        pass

    @allure.step("GET == /user/{user_id}/comment")
    def get_list_comments_by_user_id(self, user_id: str) -> CommentList:
        pass

    @allure.step("GET == /post/{post_id}/comment")
    def get_list_comments_by_post_id(self, post_id: str) -> CommentList:
        pass

    @allure.step("GET == /comment?page=*&limit=*")
    def get_list_comments(self, page: int, limit: int) -> CommentList:
        pass

    @allure.step("DELETE == /comment/{comment_id}")
    def delete_comment(self, comment_id: str) -> CommentDeleteResponseModel:
        pass
