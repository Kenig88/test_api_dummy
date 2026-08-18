# Test API Dummy

API test automation framework для публичного REST API [DummyAPI](https://dummyapi.io/).

Проект покрывает сущности `User`, `Post` и `Comment`, проверяет позитивные и негативные сценарии, поддерживает параллельный запуск, Docker, Allure и GitHub Actions.

## Стек

- Python 3.11+
- Pytest, Requests, Pydantic, Faker
- Pytest-xdist
- Allure Pytest
- Docker и Docker Compose
- GitHub Actions и GitHub Pages

## Покрытие

- создание, получение, обновление и удаление пользователей и постов;
- создание, получение и удаление комментариев;
- получение списков и проверка пагинации;
- smoke-сценарии полного жизненного цикла сущностей;
- ошибки авторизации, валидации, некорректных ID и путей;
- обращения к несуществующим ресурсам;
- проверка структуры и типов ответов через Pydantic.

Маркеры тестов:

- `smoke` — критичные end-to-end сценарии;
- `regression` — расширенные позитивные проверки;
- `negative` — проверки ошибок API.

## Структура проекта

```text
test_api_dummy/
├── tests/
│   ├── user/
│   ├── post/
│   └── comment/
├── services/
│   ├── api_base.py
│   ├── error_models.py
│   ├── user/
│   ├── post/
│   └── comment/
├── config/
│   └── base_test.py
├── utils/
│   └── helper.py
├── .github/workflows/
│   └── api-tests-dummy.yml
├── conftest.py
├── pytest.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

Основные компоненты:

- `ApiBase` централизует HTTP-запросы, timeout, безопасные retry для GET-запросов, логирование и проверку статусов;
- API-клиенты содержат операции для `User`, `Post` и `Comment`;
- endpoints-классы формируют URL;
- Pydantic-модели валидируют контракты ответов;
- payload generators создают тестовые данные;
- fixtures создают сущности и удаляют их после тестов;
- `Helper` безопасно прикрепляет запросы, ответы и transport errors к Allure.

## Подготовка окружения

Создайте виртуальное окружение:

```bash
python -m venv .venv
```

Активация в Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Активация в Linux или macOS:

```bash
source .venv/bin/activate
```

Установите зависимости:

```bash
python -m pip install -r requirements.txt
```

Создайте `.env` на основе `.env.example`:

```env
BASE_URL=https://dummyapi.io/data/v1
API_TOKEN=your_app_id_here
```

## Запуск Pytest

Проверка сбора тестов без выполнения:

```bash
python -m pytest --collect-only -q
```

Все тесты:

```bash
python -m pytest
```

Запуск по маркам:

```bash
python -m pytest -m smoke
python -m pytest -m regression
python -m pytest -m negative
```

Параллельный запуск в двух процессах:

```bash
python -m pytest -n 2
```

Марку и xdist можно комбинировать:

```bash
python -m pytest -m smoke -n 2
```

## Запуск через Docker

Соберите образ:

```bash
docker compose build
```

Запустите все тесты:

```bash
docker compose run --rm all
```

Запуск отдельных наборов:

```bash
docker compose run --rm smoke
docker compose run --rm regression
docker compose run --rm negative
```

По умолчанию Docker использует два xdist-worker. Другое количество можно передать через переменную окружения:

```bash
docker compose run --rm -e PYTEST_WORKERS=4 all
```

## Allure

Создайте результаты Allure локально:

```bash
python -m pytest --alluredir=allure-results --clean-alluredir
```

Откройте отчёт:

```bash
allure serve allure-results
```

В отчёт прикрепляются данные запросов и ответов. Чувствительные заголовки маскируются.

## GitHub Actions

Workflow `.github/workflows/api-tests-dummy.yml` запускается вручную и позволяет выбрать:

- набор `all`, `smoke`, `regression` или `negative`;
- количество xdist-worker.

Перед первым запуском добавьте в `Settings → Secrets and variables → Actions` два Repository Secret:

```text
BASE_URL
API_TOKEN
```

Для публикации Allure выберите в `Settings → Pages → Build and deployment` источник `GitHub Actions`.

Workflow выполняет тесты в Docker, сохраняет логи как artifact, публикует Allure-отчёт в GitHub Pages и хранит историю запусков в ветке `allure-history`.

## Логи и cleanup

Логи сохраняются в `logs/`. При параллельном запуске каждый worker пишет в отдельный файл:

```text
logs/api-tests-gw0.log
logs/api-tests-gw1.log
```

Созданные во время тестов сущности регистрируются в fixtures и удаляются после завершения сессии. Повторное удаление не ломает cleanup.

Локальные окружения, кеши, логи и Allure-артефакты исключены через `.gitignore`.
