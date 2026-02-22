import allure
import pytest

from config.base_test import BaseTest
from services.user.user_payloads import UserPayloads


@allure.epic("Administration")
@allure.feature("User")
@pytest.mark.smoke
class TestUserSmoke(BaseTest):

    @allure.title("Smoke: CREATE -> GET by id -> PUT -> GET by id -> DELETE -> GET by id")
    def test_user_smoke(self, api_user, created_user):
        with allure.step("test_user_smoke --> POST == /user/create"):
            user = created_user()
            user_id = str(user.id)
            assert user_id
            assert user.email
            assert user.firstName
            assert user.lastName
            assert user.dateOfBirth
            assert user.phone

        with allure.step("test_user_smoke --> GET == /user/{user_id}"):
            got = api_user.get_user_by_id(user_id)
            assert str(got.id) == user_id
            assert got.email == user.email
            assert got.firstName == user.firstName
            assert got.lastName == user.lastName
            assert got.dateOfBirth == user.dateOfBirth
            assert got.phone == user.phone

        with allure.step("test_user_smoke --> PUT == /user/{user_id}"):
            update_payload = UserPayloads.update_user_payload()
            updated_user = api_user.update_user(user_id, update_payload)
            assert str(updated_user.id) == user_id

            # это тоже самое что if внизу, только код короче и удобнее
            for field in ["firstName", "lastName", "phone"]:
                if field in update_payload:
                    assert getattr(updated_user, field) == update_payload[field]

            # if "firstName" in update_payload:
            #     assert updated_user.firstName == update_payload["firstName"]
            # if "lastName" in update_payload:
            #     assert updated_user.lastName == update_payload["lastName"]
            # if "phone" in update_payload:
            #     assert updated_user.phone == update_payload["phone"]

        with allure.step("test_user_smoke --> GET == after update /user/{user_id}"):
            got2 = api_user.get_user_by_id(user_id)

            for field in ["firstName", "lastName", "phone"]:
                if field in update_payload:
                    assert getattr(got2, field) == update_payload[field]

        with allure.step("test_user_smoke --> DELETE == /user/{user_id}"):
            deleted_user = api_user.delete_user(user_id)
            assert str(deleted_user.id) == user_id

        with allure.step("test_user_smoke --> GET == after delete should be 404"):
            err = api_user.get_user_by_id(user_id, expected_status_code=404)
            assert err.error == "RESOURCE_NOT_FOUND"
