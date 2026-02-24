import pytest
import allure
from config.base_test import BaseTest


@allure.epic("Administration")
@allure.feature("Users")
@pytest.mark.negative
class TestUsersNegative(BaseTest):
    pass
