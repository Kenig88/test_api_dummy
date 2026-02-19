from faker import Faker

fake = Faker()


class CommentPayload:

    @staticmethod
    def comment_create_payload(user_id: str, post_id: str) -> dict:
        return {
            "message": fake.text(max_nb_chars=500),
            "owner": user_id,
            "post": post_id,
        }
