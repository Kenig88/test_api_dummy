# Test API Dummy

API automation framework для тестирования публичного REST API `dummyapi.io`.

Проект демонстрирует не просто набор API-тестов, а полноценную структуру тестового фреймворка: сервисный слой, Pydantic-модели, payload generators, pytest fixtures, логирование, Allure-отчётность, Docker-запуск и CI через GitHub Actions.

---

## Стек

- Python 3.11+
- Pytest
- Requests
- Pydantic
- Faker
- Allure Pytest
- Pytest-xdist
- Docker / Docker Compose
- GitHub Actions
- GitHub Pages

---

## Что покрывает проект

Фреймворк тестирует основные сущности Dummy API:

- `User`
- `Post`
- `Comment`

Типы тестов:

- `smoke` — критичные end-to-end сценарии
- `regression` — расширенные позитивные проверки
- `negative` — ошибки авторизации, валидации, несуществующие ресурсы, неверные пути

Примеры smoke-сценариев:

```text
User:    CREATE -> GET -> UPDATE -> GET -> DELETE -> GET 404
Post:    CREATE -> GET -> UPDATE -> GET -> DELETE -> GET 404
Comment: CREATE -> GET by user -> GET by post -> DELETE -> DELETE 404
```

---

## Архитектура проекта

```text
test_api_dummy/
│
├── tests/                         # Тестовые сценарии и проверки
│   ├── user/
│   ├── post/
│   └── comment/
│
├── services/                      # Сервисный слой API-фреймворка
│   ├── api_base.py                # Единая request-логика
│   ├── user/
│   │   ├── api_user.py            # API-клиент User
│   │   ├── user_endpoints.py      # URL endpoints
│   │   ├── user_models.py         # Pydantic response-модели
│   │   └── user_payloads.py       # Генерация request body
│   ├── post/
│   │   ├── api_post.py
│   │   ├── post_endpoints.py
│   │   ├── post_models.py
│   │   └── post_payload.py
│   └── comment/
│       ├── api_comment.py
│       ├── comment_endpoints.py
│       ├── comment_models.py
│       └── comment_payload.py
│
├── utils/
│   └── helper.py                  # Безопасные Allure attachments
│
├── config/
│   └── base_test.py               # Базовый класс для тестов
│
├── conftest.py                    # Fixtures, env, session, cleanup, logging hooks
├── pytest.ini                     # Pytest config, markers, logging settings
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker image для запуска тестов
├── docker-compose.yml             # Запуск all/smoke/regression/negative suites
├── .env.example                   # Шаблон переменных окружения
└── README.md
```

---

## Главная идея архитектуры

Проект разделён на понятные слои:

```text
tests       -> сценарии и проверки
services    -> API-клиенты, endpoints, models, payloads
conftest.py -> фикстуры, env, session, cleanup, logging hooks
ApiBase     -> единая request-логика
Helper      -> Allure attachments
```

Такой подход делает тесты чистыми: тесты не собирают URL руками, не создают `requests.Session`, не думают о headers, timeout, логировании и Allure attachments. Всё это вынесено в framework layer.

---

## Почему `ApiBase` важен

`ApiBase.send_request()` — единая точка отправки запросов.

Через него централизованы:

- `timeout`
- отправка запросов через `requests.Session`
- возможность запроса без default headers для negative-тестов
- логирование метода, URL и status code
- Allure attachment response

Плюсы такого подхода:

```text
timeout централизован
Allure attach централизован
логирование централизовано
negative-тесты могут делать запрос без default headers
API-клиенты становятся короче и единообразнее
```

Пример API-клиента:

```python
response = self.send_request(
    method="POST",
    url=self.endpoint.create_user(),
    json=payload,
)
body = self._check_status_code(response, ok_statuses=[200, 201])
return UserResponseModel.model_validate(body)
```

---

## Почему нужны API-клиенты

Файлы `api_user.py`, `api_post.py`, `api_comment.py` инкапсулируют работу с API.

Тест вызывает понятный бизнес-метод:

```python
user = self.api_user.create_user(payload)
post = self.api_post.create_post(user_id=user.id)
comment = self.api_comment.create_comment(user_id=user.id, post_id=post.id)
```

А не работает напрямую с `requests`.

Это делает тесты:

- короче
- понятнее
- стабильнее
- проще для поддержки

---

## Endpoints

Endpoints вынесены в отдельные классы:

```python
class UserEndpoints:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def create_user(self) -> str:
        return f"{self.base_url}/user/create"
```

`rstrip("/")` защищает от двойных слэшей, если в `.env` случайно указать `BASE_URL` с `/` на конце.

---

## Pydantic-модели

Ответы API валидируются через Pydantic.

Это полезно, потому что тест проверяет не только отдельные поля, но и контракт ответа:

- типы данных
- обязательные поля
- структуру вложенных объектов
- формат email/date/datetime

Рекомендация по `extra`:

```text
extra="ignore"  -> нормально для response-моделей внешнего API
extra="forbid"  -> хорошо для delete/error моделей, где ожидается строгий короткий ответ
```

Почему `extra="ignore"` подходит для внешнего API: публичный API может добавить новое поле, и из-за этого тесты не должны падать, если это поле не важно для сценария.

Почему `extra="forbid"` подходит для error/delete: такие ответы обычно маленькие и предсказуемые, поэтому их можно проверять строже.

---

## Payload generators

Payloads вынесены отдельно от тестов:

```text
user_payloads.py
post_payload.py
comment_payload.py
```

Это делает тесты чище и позволяет переиспользовать генерацию данных.

Хорошая практика: генерировать уникальные данные там, где API требует уникальность.

Например, email лучше делать уникальным через `uuid`, чтобы снизить риск конфликта:

```python
email = f"test-{uuid.uuid4().hex}@example.com"
```

---

## Fixtures и cleanup

`conftest.py` отвечает за:

- загрузку `.env`
- проверку обязательных env-переменных
- создание `requests.Session`
- создание API-клиентов
- создание тестовых сущностей
- cleanup созданных сущностей
- логирование старта/финиша тестов

Пример fixture-фабрики:

```python
@pytest.fixture(scope="session")
def created_user(api_user: ApiUser):
    created_user_ids: list[str] = []

    def create_user(overrides: dict | None = None):
        payload = UserPayloads.create_user_payload()
        if overrides:
            payload.update(overrides)

        user = api_user.create_user(payload)
        created_user_ids.append(str(user.id))
        return user

    yield create_user

    for user_id in created_user_ids:
        api_user.delete_user(user_id, allow_not_found=True)
```

Почему `allow_not_found=True` полезен: если тест сам удалил сущность, cleanup не должен падать на повторном удалении.

---

## Логирование

Логирование настроено через `pytest.ini` и `conftest.py`.

Особенности:

- логи пишутся в папку `logs/`
- при запуске через `pytest-xdist` каждый worker получает отдельный лог-файл
- технический шум от `urllib3` и `faker` приглушён
- фиксируется старт и финиш каждого теста
- API-запросы логируются в `ApiBase`

Проект учитывает параллельный запуск через `pytest-xdist`: каждый worker пишет в свой log-файл, поэтому логи не перемешиваются и терминал не загрязняется подробными техническими сообщениями. Основная идея: в терминале должно быть видно краткий результат тестового прогона, а подробности лучше смотреть в `logs/` и Allure-отчёте.

Пример логов:

```text
[gw0] START TEST: tests/user/test_user_smoke.py::TestUserSmoke::test_user_smoke
POST https://dummyapi.io/data/v1/user/create -> 200
GET https://dummyapi.io/data/v1/user/{id} -> 200
[gw0] END TEST: tests/user/test_user_smoke.py::TestUserSmoke::test_user_smoke -> PASSED
```

---

## Allure

Проект использует Allure для отчётности.

Используются:

- `@allure.epic`
- `@allure.feature`
- `@allure.title`
- `allure.step`
- attachments response/request data

`Helper.attach_response_safe()` сделан безопасным: если attachment по какой-то причине не сработает, тест не должен падать из-за проблемы отчёта.

---

## Переменные окружения

Создайте локальный `.env` на основе `.env.example`:

```env
BASE_URL=https://dummyapi.io/data/v1
API_TOKEN=your_app_id_here
```

`.env` не должен попадать в git.

В GitHub Actions эти значения нужно добавить в:

```text
Settings -> Secrets and variables -> Actions -> Repository secrets
```

Нужные secrets:

```text
BASE_URL
API_TOKEN
```

---

## Локальный запуск

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Сбор тестов без запуска:

```bash
pytest --collect-only -q
```

Запуск всех тестов:

```bash
pytest
```

Запуск smoke:

```bash
pytest -m smoke
```

Запуск regression:

```bash
pytest -m regression
```

Запуск negative:

```bash
pytest -m negative
```

Параллельный запуск:

```bash
pytest -n 2
```

---

## Параллельный запуск через pytest-xdist

В проект встроен `pytest-xdist`, поэтому тесты можно запускать параллельно в несколько workers. Это полезно, когда тестов становится больше: pytest распределяет тесты между несколькими процессами, и общий прогон может выполняться быстрее.

Обычный запуск:

```bash
pytest
```

Параллельный запуск в 2 workers:

```bash
pytest -n 2
```

Параллельный запуск в 4 workers:

```bash
pytest -n 4
```

Автоматический выбор количества workers:

```bash
pytest -n auto
```

При запуске через `pytest-xdist` каждый worker получает отдельное имя, например `gw0`, `gw1`, `gw2`. В проекте это учтено в логировании: каждый worker пишет в отдельный файл.

Пример:

```text
logs/api-tests-gw0.log
logs/api-tests-gw1.log
logs/api-tests-gw2.log
```

Так логи не смешиваются в один нечитаемый файл.

Через Docker количество workers можно передать через переменную окружения:

```bash
PYTEST_WORKERS=4 docker compose run --rm smoke
```

В GitHub Actions количество workers также можно выбрать вручную при запуске workflow.

---

## Локальный Allure report

Запуск тестов с генерацией Allure results:

```bash
pytest --alluredir=allure-results --clean-alluredir
```

Генерация HTML-отчёта:

```bash
allure generate allure-results -o allure-report --clean
```

Просмотр отчёта:

```bash
allure serve allure-results
```

---

## Запуск через Docker

Сборка Docker image:

```bash
docker compose build
```

Запуск всех тестов:

```bash
docker compose run --rm all
```

Запуск отдельных suites:

```bash
docker compose run --rm smoke
docker compose run --rm regression
docker compose run --rm negative
```

Количество workers можно менять через env:

```bash
PYTEST_WORKERS=4 docker compose run --rm smoke
```

---

## GitHub Actions CI

Workflow позволяет вручную выбрать:

- suite: `all`, `smoke`, `regression`, `negative`
- количество xdist workers: `auto`, `2`, `3`, `4`

CI делает:

1. Checkout repository
2. Build Docker image
3. Run selected test suite
4. Upload logs
5. Install Allure CLI
6. Restore Allure history
7. Generate Allure HTML report
8. Publish report to GitHub Pages
9. Persist Allure history
10. Fail workflow if tests failed

Важно: тестовый шаг использует `continue-on-error: true`, чтобы даже при падении тестов успеть сохранить логи и Allure-отчёт. В конце workflow всё равно падает, если тесты реально упали.

---

## GitHub Pages и Allure history

После CI-запуска Allure report публикуется в GitHub Pages:

```text
https://<your-username>.github.io/<repository-name>/
```

История запусков сохраняется в отдельной ветке `allure-history`, чтобы работал график:

```text
Graphs -> Trend
```

---

## Проверки качества перед коммитом

Перед коммитом полезно запускать:

```bash
python -m compileall -q services tests conftest.py config utils
pytest --collect-only -q
pytest -m smoke
ruff check services config tests conftest.py utils
pip check
```

Если всё прошло, проект в хорошем состоянии.

---

## Что не нужно коммитить

Не должны попадать в git:

```text
.env
.venv/
.idea/
.pytest_cache/
.ruff_cache/
__pycache__/
logs/
allure-results/
allure-report/
```

Для отправки чистого архива можно использовать:

```bash
git archive --format=zip -o test_api_dummy_clean.zip HEAD
```

---

## Что демонстрирует этот проект

Этот проект показывает навыки:

- проектирования API test framework
- работы с pytest fixtures
- сервисного слоя для API-клиентов
- валидации API responses через Pydantic
- генерации тестовых данных
- позитивных, smoke, regression и negative тестов
- параллельного запуска тестов через pytest-xdist
- логирования API-тестов
- Allure reporting
- Docker execution
- GitHub Actions CI
- публикации отчётов в GitHub Pages

---

## Полезные принципы для следующего API framework

1. Тесты должны быть короткими и читатьcя как сценарии.
2. API-запросы не должны жить прямо в тестах.
3. URL лучше держать в endpoints-классах.
4. Request body лучше генерировать через payload-фабрики.
5. Response body лучше валидировать через Pydantic-модели.
6. Timeout, logging и Allure attachments лучше централизовать в `ApiBase`.
7. Тестовые данные нужно удалять через cleanup.
8. Negative-тестам иногда нужен запрос без default headers.
9. Параллельный запуск через `pytest-xdist` нужно учитывать в логах и cleanup.
10. Docker нужен для одинакового запуска локально и в CI.
11. README должен объяснять не только как запустить проект, но и почему он устроен именно так.
