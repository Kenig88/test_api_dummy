import allure
import pytest

from config.base_test import BaseTest
from services.post.post_payloads import PostPayloads


@allure.epic("Administration")
@allure.feature("Post")
@pytest.mark.regression
class TestPostRegression(BaseTest):
    @allure.title("TestPostRegression --> test_create_post()")
    def test_create_post(self, created_user, created_post):
        user = created_user()
        user_id = str(user.id)
        payload = PostPayloads.create_post_payload(user_id)
        post = created_post(user_id=user_id, overrides=payload)

        assert post.id
        assert post.text == payload["text"]
        assert post.image == payload["image"]
        assert post.likes == payload["likes"]
        assert post.tags == payload["tags"]
        assert post.owner.id == user_id

    @allure.title("TestPostRegression --> test_get_list_posts_by_user_id()")
    def test_get_list_posts_by_user_id(self, created_post, created_user):
        user = created_user()
        user_id = str(user.id)
        post_created = created_post(user_id)

        page = 0
        limit = 50

        response = self.api_post.get_list_posts_by_user_id(
            user_id=user_id,
            page=page,
            limit=limit,
        )
        assert response is not None
        assert response.page == page
        assert response.limit == limit
        assert response.total is not None
        assert isinstance(response.data, list)
        assert len(response.data) <= limit
        assert all(post.owner.id == user_id for post in response.data)
        assert any(post.id == post_created.id for post in response.data)

    @allure.title("TestPostRegression --> test_get_list_posts()")
    def test_get_list_posts(self):
        page = 0
        limit = 50

        response = self.api_post.get_list_posts(
            page=page,
            limit=limit,
        )
        assert response is not None
        assert response.page == page
        assert response.limit == limit
        assert response.total is not None
        assert isinstance(response.data, list)
        assert len(response.data) <= limit
        if response.data:
            assert all(post.id is not None for post in response.data)

    @allure.title("TestPostRegression --> test_get_post_by_id()")
    def test_get_post_by_id(self, created_post):
        post = created_post()
        got = self.api_post.get_post_by_id(post.id)
        assert got.id == post.id
        assert got.image == post.image
        assert got.likes == post.likes
        assert got.link == post.link
        assert got.tags == post.tags
        assert got.text == post.text
        assert got.publishDate == post.publishDate
        assert got.updatedDate == post.updatedDate
        assert got.owner.id == post.owner.id
        assert got.owner.firstName == post.owner.firstName
        assert got.owner.lastName == post.owner.lastName

    @allure.title("TestPostRegression --> test_update_post()")
    def test_update_post(self, created_post):
        post = created_post()
        update_payload = PostPayloads.update_post_payload()
        updated_post = self.api_post.update_post(post.id, update_payload)

        assert updated_post.text == update_payload["text"]
        assert updated_post.image == update_payload["image"]
        assert updated_post.likes == update_payload["likes"]
        assert updated_post.tags == update_payload["tags"]
        assert updated_post.id == post.id
        assert updated_post.link == post.link
        assert updated_post.publishDate == post.publishDate
        assert updated_post.updatedDate > post.updatedDate
        assert updated_post.owner.id == post.owner.id
        assert updated_post.owner.firstName == post.owner.firstName
        assert updated_post.owner.lastName == post.owner.lastName

    @allure.title("TestPostRegression --> test_delete_post()")
    def test_delete_post(self, created_post):
        post = created_post()
        deleted_post = self.api_post.delete_post(post.id)
        assert deleted_post.id == post.id

        err = self.api_post.get_post_by_id(post.id, expected_status_code=404)
        assert err.error == "RESOURCE_NOT_FOUND"
