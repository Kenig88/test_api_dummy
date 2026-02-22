import pytest
from services.user.api_user import ApiUser
from services.post.api_post import ApiPost
from services.comment.api_comment import ApiComment


class BaseTest:
    api_user: ApiUser
    api_post: ApiPost
    api_comment: ApiComment

    @pytest.fixture(autouse=True)
    def _init_clients(self, api_user: ApiUser, api_post: ApiPost, api_comment: ApiComment):
        self.api_user = api_user
        self.api_post = api_post
        self.api_comment = api_comment
