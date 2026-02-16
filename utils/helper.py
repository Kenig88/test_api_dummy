import allure
import requests


class Helper:
    """Минимальный helper: прикрепляет ответ к Allure и не падает."""

    def attach_response_safe(self, resp: requests.Response) -> None:
        # 1) Короткая информация о запросе
        try:
            req = resp.request
            allure.attach(
                f"{req.method} {req.url}",
                name="Request",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception:
            # Если вдруг request недоступен — просто не прикрепляем
            pass

        # 2) Тело ответа (JSON или текст)
        try:
            body = resp.json()
        except Exception:
            body = resp.text

        # 3) Прикрепляем статус + body
        try:
            allure.attach(
                f"Status: {resp.status_code}\n\nBody:\n{body}",
                name="Response",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception:
            # Главное правило: helper не должен ломать тест
            pass
