import allure
import pytest

from config.base_test import BaseTest
from services.post.post_payload import PostPayload


@allure.epic("Administration")
@allure.feature("Post")
@pytest.mark.regression
class TestPostRegression(BaseTest):

    @allure.title("TestPostRegression --> test_create_post()")
    def test_create_post(self, created_post):
        post = created_post()
        assert post.id is not None
        assert post.text is not None
        assert post.image is not None
        assert post.likes is not None
        assert post.tags is not None
        assert post.owner is not None

    @allure.title("TestPostRegression --> test_get_list_posts_by_user_id()")
    def test_get_list_posts_by_user_id(self, created_post, created_user):
        user = created_user()
        user_id = user.id
        post_created = created_post(user_id)

        page = 0
        limit = 50

        response = self.api_post.get_list_posts_by_user_id(
            user_id=user_id,
            page=page,
            limit=limit
        )
        assert response is not None
        assert all(p.owner.id == user_id for p in response.data)
        assert response.page == page
        assert response.limit == limit
        assert response.total is not None
        assert isinstance(response.data, list)
        assert len(response.data) <= limit  # контракт пагинации
        if response.data:
            assert all(p.id is not None for p in response.data)
            assert any(p.id == post_created.id for p in response.data)

    @allure.title("TestPostRegression --> test_get_list_posts()")
    def test_get_list_posts(self):
        page = 0
        limit = 50

        response = self.api_post.get_list_posts(
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
            assert all(p.id is not None for p in response.data)

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
        update_payload = PostPayload.update_post_payload()
        updated_post = self.api_post.update_post(post.id, update_payload)

        # измененные поля сравниваю с update_payload
        assert updated_post.text == update_payload['text']
        assert updated_post.image == update_payload['image']
        assert updated_post.likes == update_payload['likes']
        assert updated_post.tags == update_payload['tags']

        # неизмененные поля сравниваю с post
        assert updated_post.id == post.id
        assert updated_post.link == post.link
        assert updated_post.publishDate == post.publishDate
        assert updated_post.updatedDate >= post.updatedDate
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
