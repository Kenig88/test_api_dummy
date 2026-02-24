import allure
import pytest

from config.base_test import BaseTest
from services.post.post_payload import PostPayload


@allure.epic("Administration")
@allure.feature("Post")
@pytest.mark.smoke
class TestPostSmoke(BaseTest):

    @allure.title("Smoke: CREATE -> GET by id -> PUT -> GET by id -> DELETE -> GET by id")
    def test_post_smoke(self, created_user, created_post):
        with allure.step("test_post_smoke --> POST == /post/create"):
            user = created_user()
            user_id = str(user.id)
            post = created_post(user_id=user_id)
            post_id = str(post.id)
            # ниже проверяю данные из PostPayload
            assert post_id
            assert post.text
            assert post.image
            assert isinstance(post.likes, int) # единственный int
            assert post.tags
            assert post.owner.id == user_id

        with allure.step("test_post_smoke --> GET == /post/{post_id}"):
            got = self.api_post.get_post_by_id(post_id)
            assert got.id == post_id
            assert got.text == post.text
            assert got.image == post.image
            assert isinstance(got.likes, int) # единственный int
            assert got.tags == post.tags
            assert got.owner.id == user_id

        with allure.step("test_post_smoke --> PUT == /post/{post_id}"):
            update_payload = PostPayload.update_post_payload()
            updated_post = self.api_post.update_post(post_id, update_payload)
            assert updated_post.id == post_id

            for field in ["text", "image", "likes", "tags"]:
                if field in update_payload:
                    assert getattr(updated_post, field) == update_payload[field]

        with allure.step("test_post_smoke --> GET == after update /post/{post_id}"):
            got2 = self.api_post.get_post_by_id(post_id)
            for field in ["text", "image", "likes", "tags"]:
                if field in update_payload:
                    assert getattr(got2, field) == update_payload[field]

        with allure.step("test_post_smoke --> DELETE == /post/{post_id}"):
            deleted_post = self.api_post.delete_post(post_id)
            assert deleted_post.id == post_id

        with allure.step("test_post_smoke --> GET == after delete should be 404"):
            err = self.api_post.get_post_by_id(post_id, expected_status_code=404)
            assert err.error == "RESOURCE_NOT_FOUND"
