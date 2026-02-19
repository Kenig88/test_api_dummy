from attr.validators import max_len
from faker import Faker

fake = Faker()


class PostPayload:

    @staticmethod
    def post_payload(user_id: str) -> dict:
        return {
            "text": fake.text(max_len(20)),
            "image": fake.image(image_format='jpg'),
            "likes": fake.random_int(min=1, max=1000),
            "tags": [fake.word()],
            "owner": user_id,
        }
