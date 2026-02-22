from attr.validators import max_len
from faker import Faker

fake = Faker()


class PostPayload:

    @staticmethod
    def create_post_payload(user_id: str) -> dict:
        return {
            "text": fake.text(max_nb_chars=20),
            "image": fake.image_url(),
            "likes": fake.random_int(min=1, max=1000),
            "tags": [fake.word()],
            "owner": user_id,
        }

    @staticmethod
    def update_post_payload() -> dict:
        return {
            "text": fake.text(max_nb_chars=20),
            "image": fake.image_url(),
            "likes": fake.random_int(min=1, max=1000),
            "tags": [fake.word()],
        }
