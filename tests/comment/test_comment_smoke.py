import allure
import pytest

from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Comment")
@pytest.mark.smoke
class TestCommentSmoke(BaseTest):
    @allure.title("Smoke: CREATE -> GET by user_id -> GET by post_id -> DELETE -> DELETE again")
    def test_comment_smoke(self, created_user, created_post, created_comment):
        user = created_user()
        post = created_post(user_id=str(user.id))
        comment = created_comment(user_id=str(user.id), post_id=str(post.id))

        with allure.step("test_comment_smoke -> POST == /comment/create"):
            comment_id = str(comment.id)
            assert comment_id
            assert comment.message
            assert comment.owner
            assert comment.post == post.id

        with allure.step("test_comment_smoke -> GET == /user/{user_id}/comment"):
            response_user = self.api_comment.get_list_comments_by_user_id(
                user_id=user.id,
                page=0,
                limit=10,
            )
            comments_user = response_user.data
            comment_by_user = next((item for item in comments_user if item.id == comment_id), None)
            assert comment_by_user is not None
            assert comment_by_user.owner.id == user.id
            assert comment_by_user.post == post.id
            assert comment_by_user.message == comment.message
            assert response_user.page == 0
            assert response_user.limit == 10
            assert response_user.total >= 1

        with allure.step("test_comment_smoke -> GET == /post/{post_id}/comment"):
            response_post = self.api_comment.get_list_comments_by_post_id(
                post_id=post.id,
                page=0,
                limit=15,
            )
            comments_post = response_post.data
            comment_by_post = next((item for item in comments_post if item.id == comment_id), None)
            assert comment_by_post is not None
            assert comment_by_post.owner.id == user.id
            assert comment_by_post.post == post.id
            assert comment_by_post.message == comment.message
            assert response_post.page == 0
            assert response_post.limit == 15
            assert response_post.total >= 1

        with allure.step("test_comment_smoke -> DELETE == /comment/{comment_id}"):
            deleted_comment = self.api_comment.delete_comment(comment_id)
            assert deleted_comment.id == comment_id

        with allure.step("test_comment_smoke -> DELETE again after delete should be 404"):
            err = self.api_comment.delete_comment(comment_id, expected_status_code=404)
            assert err.error == "RESOURCE_NOT_FOUND"
