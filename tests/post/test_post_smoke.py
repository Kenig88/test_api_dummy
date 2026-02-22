import allure
import pytest

from config.base_test import BaseTest
from services.post.post_payload import PostPayload


@allure.epic("Administration")
@allure.feature("Post")
@pytest.mark.smoke
class TestPostSmoke(BaseTest):

    @allure.title("Smoke: CREATE -> GET by id -> PUT -> GET by id -> DELETE -> GET by id")
    def test_post_smoke(self, api_post, created_post):
        with allure.step("test_post_smoke --> POST == /post/create"):
            post = created_post()
            post_id = str(post.id)
            assert post_id
            assert post.text
            assert post.image
            assert post.likes
            assert post.tags
            assert post.owner

        with allure.step("test_post_smoke --> GET == /post/{post_id}"):
            got = api_post.get_post_by_id(post_id)
            assert str(got.id) == post_id
            assert got.text == post.text
            assert got.image == post.image
            assert got.likes == post.likes
            assert got.tags == post.tags
            assert got.owner == post.owner

        with allure.step("test_post_smoke --> PUT == /post/{post_id}"):
            update_payload = PostPayload.update_post_payload()
            updated_post = api_post.update_post(post_id, update_payload)
            assert str(updated_post.id) == post_id

            for field in ["text", "image", "likes", "tags"]:
                if field in update_payload:
                    assert getattr(updated_post, field) == update_payload[field]

        with allure.step("test_post_smoke --> GET == after update /post/{post_id}"):
            got2 = api_post.get_post_by_id(post_id)
            for field in ["text", "image", "likes", "tags"]:
                if field in update_payload:
                    assert getattr(got2, field) == update_payload[field]

        with allure.step("test_post_smoke --> DELETE == /post/{post_id}"):
            deleted_post = api_post.delete_post(post_id)
            assert str(deleted_post.id == post_id)

        with allure.step("test_post_smoke --> GET == after delete should be 404"):
            err = api_post.get_post_by_id(post_id, expected_status_code=404)
            assert err.error == "RESOURCE_NOT_FOUND"
