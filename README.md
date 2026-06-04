# <p align="center"> 📦 Test API Dummy </p>

Проект автоматизации API-тестирования, построенный с использованием:

🐍 Python + Pytest

🐳 Docker + Docker Compose

📊 Allure Report

🚀 GitHub Actions (CI)

🌐 GitHub Pages (автоматическая публикация отчётов с историей)

---

# <p align="center"> - Описание проекта - </p>

Этот проект демонстрирует полноценный фреймворк для API-автоматизации, включающий:

- Структурированный сервисный слой (API-клиенты)

- Pydantic-модели для валидации ответов

- Фикстуры с автоматической очисткой тестовых данных

- Allure-отчёты с прикреплением запросов и ответов

- Логирование действий через pytest logging

- Параллельный запуск тестов

- Docker-исполнение тестов

- CI-пайплайн с выбором test suite

- Сохранение истории Allure (Trend graph)

В качестве тестового окружения используется dummy REST API.

---

# <p align="center"> - Структура проекта - </p>

```text
test_api_dummy/                  # Корневая папка проекта (репозиторий)
│
├── services/                    # Сервисный слой: всё, что связано с работой с API (клиенты, endpoints, модели, payloads)
├── tests/                       # Тесты pytest: test cases, фикстуры, маркеры smoke/regression/negative и т.д.
│
├── conftest.py                  # Фикстуры (hooks, setup/teardown)
├── pytest.ini                   # Конфигурация pytest
├── requirements.txt             # Python-зависимости проекта (pytest, requests, allure, pydantic и т.п.)
│
├── Dockerfile                   # Инструкция сборки Docker-образа с окружением и зависимостями для запуска тестов
├── docker-compose.yml           # Набор docker-compose сервисов для запуска разных suite (all/smoke/regression/negative)
│
├── .env.example                 # Пример файла переменных окружения (BASE_URL, API_TOKEN) — шаблон для локального запуска
└── README.md                    # Описание проекта: как запускать локально/в CI, где смотреть Allure отчёт и историю
```

---

# <p align="center"> - Переменные окружения - </p>

Создайте файл .env на основе .env.example:

```text
BASE_URL=https://your-api-url.com
API_TOKEN=your_api_token_here
```

Все переменные окружения передаются через Docker и GitHub Secrets в CI.

---

# <p align="center"> 🧪 Локальный запуск без Docker. </p>

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Запуск тестов (пример):

```bash
pytest tests/post/test_post_smoke.py
```

Параллельный запуск (пример):

```bash
pytest tests/post/test_post_smoke.py -n 2
```

---

# <p align="center"> 🐳 Локальный запуск тестов через Docker. </p>

Создание окружения Docker image перед тестами:

```bash
docker compose build
```

Запуск всех тестов:

```bash
docker compose run --rm all
```

Запуск отдельных наборов тестов:

```bash
docker compose run --rm smoke
docker compose run --rm regression
docker compose run --rm negative
```

---

# <p align="center"> 📊 Генерация Allure-отчёта локально. </p>

Локальный запуск тестов с созданием Allure-отчёта:

```bash
pytest --alluredir=allure-results
```

Для генерации статического отчёта:

```bash
allure generate allure-results -o allure-report --clean
```

Для просмотра отчёта локально:

```bash
allure serve allure-results
```

---

# <p align="center"> 🚀 CI: GitHub Actions + Allure + Pages. </p>

Проект включает полностью автоматизированный CI-пайплайн.

**Возможности CI**:

- Ручной запуск workflow

- Выбор набора тестов (all / smoke / regression / negative)

- Запуск тестов в Docker

- Генерация Allure HTML

- Автоматическая публикация отчёта в GitHub Pages

- Сохранение истории Allure (Trend graph)

---

# <p align="center">  ▶ Как запустить CI. </p>

0. Перейдите в GitHub -> Settings -> Secrets and variables -> Actions и добавьте секреты "API_TOKEN" и "BASE_URL" 
1. Перейдите в GitHub → Actions
2. Выберите workflow:

```text
API Tests
```

3. Нажмите Run workflow
4. Выберите suite
5. Запустите выполнение

---

# <p align="center"> 🌐 Онлайн-отчёт Allure. </p>

После каждого запуска CI отчёт автоматически публикуется в GitHub Pages.

Доступен по адресу:

```text
https://<your-username>.github.io/<repository-name>/
```

---

# <p align="center"> 📈 История запусков (Allure Trend). </p>

Проект сохраняет историю запусков между CI-прогонами.

Чтобы посмотреть динамику:

1. Откройте опубликованный отчёт
2. Перейдите в:

```text
Graphs → Trend
```

3. Отобразится статистика выполнения тестов по нескольким запускам

---

# <p align="center"> 🧠 Особенности фреймворка. </p>

🔹 Сервисный слой:

Все API-запросы инкапсулированы в сервисных классах (ApiUser, ApiPost и ApiComment),
что делает тесты чистыми и читаемыми.

🔹 Валидация через Pydantic:

Ответы API валидируются с помощью типизированных моделей, что повышает надёжность проверок.

🔹 Автоматическая очистка данных:

Фикстуры создают и удаляют сущности автоматически, обеспечивая изоляцию тестов.

🔹 Параллельный запуск:

Поддержка pytest-xdist.

🔹 Логирование:

Логирование действий пользователя и навигации через pytest logging с выводом в файл.

🔹 Безопасные Allure-прикрепления:

Запросы и ответы прикрепляются к отчёту без риска уронить тест при ошибке attachment.

🔹 Docker-исполнение:

Обеспечивает одинаковое поведение тестов в любом окружении.

---

# <p align="center"> 🔒 Безопасность. </p>

* .env исключён из коммитов через .gitignore

* Секреты хранятся в GitHub Actions Secrets

* В CI не используются реальные production-токены

---

# <p align="center"> 🏆 Что демонстрирует этот проект. </p>

* Архитектуру API-автотестов

* Интеграцию CI/CD

* Docker-исполнение

* Allure-отчёты с историей

* Публичную публикацию отчётов через GitHub Pages

* Чистую структуру и разделение ответственности
