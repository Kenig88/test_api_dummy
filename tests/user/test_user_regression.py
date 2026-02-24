import allure
import pytest

from config.base_test import BaseTest
from services.user.user_payloads import UserPayloads


@allure.epic("Administration")
@allure.feature("User")
@pytest.mark.regression
class TestUserRegression(BaseTest):

    @allure.title("TestUserRegression --> test_create_user()")
    def test_create_user(self, created_user):
        user = created_user()
        assert user.id is not None
        assert user.email is not None
        assert user.firstName is not None
        assert user.lastName is not None
        assert user.dateOfBirth is not None
        assert user.phone is not None

    @allure.title("TestUserRegression --> test_get_list_users()")
    def test_get_list_users(self):
        page = 0
        limit = 50

        response = self.api_user.get_list_users(
            page=page,
            limit=limit
        )
        assert response is not None
        assert response.page == page
        assert response.limit == limit
        assert response.total is not None
        assert isinstance(response.data, list)
        assert len(response.data) <= limit # контракт пагинации
        if response.data:
            assert all(user.id is not None for user in response.data)

    @allure.title("TestUserRegression --> test_get_user_by_id(user_id)")
    def test_get_user_by_id(self, created_user):
        user = created_user()
        got = self.api_user.get_user_by_id(user.id)
        assert got.id == user.id
        assert got.firstName == user.firstName
        assert got.lastName == user.lastName
        assert got.email == user.email
        assert got.dateOfBirth == user.dateOfBirth
        assert got.phone == user.phone
        assert got.registerDate == user.registerDate
        assert got.updatedDate == user.updatedDate

    @allure.title("TestUserRegression --> test_update_user()")
    def test_update_user(self, created_user):
        user = created_user()
        update_payload = UserPayloads.update_user_payload()
        updated_user = self.api_user.update_user(user.id, update_payload)

        # измененные поля сравниваю с update_payload
        assert updated_user.firstName == update_payload['firstName']
        assert updated_user.lastName == update_payload['lastName']
        assert updated_user.phone == update_payload['phone']

        # неизмененные поля сравниваю с user
        assert updated_user.id == user.id
        assert updated_user.dateOfBirth == user.dateOfBirth
        assert updated_user.email == user.email
        assert updated_user.registerDate == user.registerDate
        assert updated_user.updatedDate >= user.updatedDate

    @allure.title("TestUserRegression --> test_delete_user()")
    def test_delete_user(self, created_user):
        user = created_user()
        deleted_user = self.api_user.delete_user(user.id)
        assert deleted_user.id == user.id

        err = self.api_user.get_user_by_id(user.id, expected_status_code=404)
        assert err.error == "RESOURCE_NOT_FOUND"
