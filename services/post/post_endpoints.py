class PostEndpoints:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def create_post(self) -> str:
        return f"{self.base_url}/post/create"

    def get_list_posts(self) -> str:
        return f"{self.base_url}/post"

    def get_list_posts_by_user_id(self, user_id: str) -> str:
        return f"{self.base_url}/user/{user_id}/post"

    def get_post_by_post_id(self, post_id: str) -> str:
        return f"{self.base_url}/post/{post_id}"

    def update_post(self, post_id: str) -> str:
        return f"{self.base_url}/post/{post_id}"

    def delete_post(self, post_id: str) -> str:
        return f"{self.base_url}/post/{post_id}"
