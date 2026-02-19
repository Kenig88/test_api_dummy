class CommentEndpoints:
    def __init__(self, base_url):
        self.base_url = base_url

    def create_comment(self) -> str:
        return f"{self.base_url}/comment/create"

    def get_list_comments_by_user_id(self, user_id: str) -> str:
        return f"{self.base_url}/user/{user_id}/comment"

    def get_list_comments_by_post_id(self, post_id: str) -> str:
        return f"{self.base_url}/post/{post_id}/comment"

    def get_list_comments(self) -> str:
        return f"{self.base_url}/comment"

    def delete_comment(self, comment_id: str) -> str:
        return f"{self.base_url}/comment/{comment_id}"
