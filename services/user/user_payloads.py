import uuid
from faker import Faker

fake = Faker()


class UserPayloads:

    @staticmethod
    def create_user_payload() -> dict:
        unique_email = f"autotest{uuid.uuid4().hex[:8]}@gmail.com"

        return {
            "email": unique_email,
            "firstName": fake.first_name(),
            "lastName": fake.last_name(),
            "dateOfBirth": fake.dateOfBirth(),
            "phone": fake.numerify("###-###-####"),
        }

    @staticmethod
    def update_user_payload() -> dict:
        return {
            "firstName": fake.first_name(),
            "lastName": fake.lastName(),
            "phone": fake.numerify("###-###-####"),
        }
