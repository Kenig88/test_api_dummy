import allure
import pytest

from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Comment")
@pytest.mark.regression
class TestCommentRegression(BaseTest):

    @allure.step("TestCommentRegression --> test_create_comment()")
    def test_create_comment(self, created_comment):
        comment = created_comment()
        assert comment.id is not None
        assert comment.owner is not None
        assert comment.post is not None
        assert comment.message is not None

    @allure.step("TestCommentRegression --> test_get_list_comments_by_user_id()")
    def test_get_list_comments_by_user_id(self, created_comment, created_user, created_post):
        user = created_user()
        user_id = user.id
        post = created_post()
        post_id = post.id
        comment_created = created_comment(user_id, post_id)

        page = 0
        limit = 50

        response = self.api_comment.get_list_comments_by_user_id(
            user_id=user_id,
            page=page,
            limit=limit
        )
        assert response is not None
        assert all(c.owner.id == user_id for c in response.data)
        assert response.page == page
        assert response.limit == limit
        assert response.total is not None
        assert isinstance(response.data, list)
        assert len(response.data) <= limit  # контракт пагинации
        if response.data:
            assert all(c.id is not None for c in response.data)
            assert any(c.id == comment_created.id for c in response.data)

    @allure.step("TestCommentRegression --> test_get_list_comments_by_post_id()")
    def test_get_list_comments_by_post_id(self, created_comment, created_user, created_post):
        user = created_user()
        user_id = user.id
        post = created_post()
        post_id = post.id
        comment_created = created_comment(user_id, post_id)

        page = 0
        limit = 50

        response = self.api_comment.get_list_comments_by_post_id(
            post_id=post_id,
            page=page,
            limit=limit
        )
        assert response is not None
        assert all(c.post == post_id for c in response.data)
        assert response.page == page
        assert response.limit == limit
        assert response.total is not None
        assert isinstance(response.data, list)
        assert len(response.data) <= limit  # контракт пагинации
        if response.data:
            assert all(c.id is not None for c in response.data)
            assert any(c.id == comment_created.id for c in response.data)

    @allure.step("TestCommentRegression --> test_get_list_comments()")
    def test_get_list_comments(self):
        page = 0
        limit = 50

        response = self.api_comment.get_list_comments(
            page=page,
            limit=limit
        )
        assert response is not None
        assert response.page == page
        assert response.limit == limit
        assert response.total is not None
        assert isinstance(response.data, list)
        assert len(response.data) <= limit  # контракт пагинации
        if response.data:
            assert all(c.id is not None for c in response.data)

    @allure.step("TestCommentRegression --> test_delete_comment()")
    def test_delete_comment(self, created_comment):
        comment = created_comment()
        deleted_comment = self.api_comment.delete_comment(comment.id)
        assert deleted_comment.id == comment.id

        err = self.api_comment.delete_comment(comment.id)
        assert err.error == "RESOURCE_NOT_FOUND"
