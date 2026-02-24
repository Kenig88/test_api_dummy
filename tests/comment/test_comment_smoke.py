import allure
import pytest

from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Comment")
@pytest.mark.smoke
class TestCommentSmoke(BaseTest):

    @allure.title("Smoke: CREATE -> GET by user_id -> GET by post_id -> DELETE -> verify DELETE")
    def test_comment_smoke(self, created_user, created_post, created_comment):
        user = created_user()
        post = created_post(user_id=str(user.id))
        comment = created_comment(user_id=str(user.id), post_id=str(post.id))

        with allure.step("test_comment_smoke -> POST == /comment/create"):
            comment_id = str(comment.id)
            assert comment_id
            assert comment.message
            assert comment.owner
            assert str(comment.post)

        with allure.step("test_comment_smoke -> GET == /user/{user_id}/comment"):
            response_user = self.api_comment.get_list_comments_by_user_id(
                user_id=str(user.id),
                page=0,
                limit=10
            )
            comments_user = response_user.data
            assert any(comment.id == comment_id for comment in comments_user)
            assert any(comment.owner.id == str(user.id) for comment in comments_user)
            assert response_user.page == 0
            assert response_user.limit == 10
            assert response_user.total >= 1

        with allure.step("test_comment_smoke -> GET == /post/{post_id}/comment"):
            response_post = self.api_comment.get_list_comments_by_post_id(
                post_id=str(post.id),
                page=0,
                limit=15
            )
            comments_post = response_post.data
            assert any(comment.id == comment_id for comment in comments_post)
            assert any(comment.post == post.id for comment in comments_post)
            assert response_post.page == 0
            assert response_post.limit == 15
            assert response_post.total >= 1

        with allure.step("test_comment_smoke -> DELETE == /comment/{comment_id}"):
            deleted_comment = self.api_comment.delete_comment(comment_id)
            assert deleted_comment.id == comment_id

        with allure.step("test_comment_smoke -> GET == after delete should be 404"):
            err = self.api_comment.delete_comment(comment_id)
            assert err.error == "RESOURCE_NOT_FOUND"
