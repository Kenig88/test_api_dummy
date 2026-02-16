import allure
import requests


class Helper:
    """Минимальный helper: прикрепляет ответ к Allure и не падает."""

    def attach_response_safe(self, response: requests.Response) -> None:
        # 1) Короткая информация о запросе
        try:
            request = response.request
            allure.attach(
                f"{request.method} {request.url}",
                name="Requests",
                attachment_type=allure.attachment_type.TEXT
            )
        except Exception:
            #  Если вдруг request недоступен — просто не прикрепляем
            pass

        # 2) Тело ответа (JSON или текст)
        try:
            body = response.json()
        except Exception:
            body = response.text

        # 3) Прикрепляем статус + body
        try:
            allure.attach(
                f"Status code: {response.status_code}\n\nBody: {body}",
                name="Response",
                attachment_type=allure.attachment_type.TEXT
            )
        except Exception:
            # Главное правило: helper не должен ломать тест
            pass
