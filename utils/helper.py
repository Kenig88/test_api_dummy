import allure
import requests


class Helper:
    """Helper: безопасно прикрепляет API-ответы к Allure."""

    def attach_response_safe(self, response: requests.Response) -> None:
        """
        Прикрепляет к Allure краткую информацию об API-запросе и ответе.

        Метод не должен ломать тесты и защищает от повторного прикрепления
        одного и того же response.
        """
        if getattr(response, "_allure_attached", False):
            return

        try:
            request = response.request
            allure.attach(
                f"{request.method} {request.url}",
                name="Request",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception:
            pass

        try:
            body = response.json()
        except Exception:
            body = response.text

        try:
            allure.attach(
                (
                    f"Status code: {response.status_code}\n"
                    f"Response time: {response.elapsed.total_seconds():.3f} sec\n\n"
                    f"Body: {body}"
                ),
                name="Response",
                attachment_type=allure.attachment_type.TEXT,
            )
            setattr(response, "_allure_attached", True)
        except Exception:
            pass