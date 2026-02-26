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

- Docker-исполнение тестов

- CI-пайплайн с выбором test suite

- Сохранение истории Allure (Trend graph)

В качестве тестового окружения используется dummy REST API.

---

# <p align="center"> - Структура проекта - </p>

```text
test_api_dummy/                 # Корневая папка проекта (репозиторий)
│
├── services/                    # Сервисный слой: всё, что связано с работой с API (клиенты, endpoints, модели, payloads)
├── tests/                       # Тесты pytest: test cases, фикстуры, маркеры smoke/regression/negative и т.д.
├── Dockerfile                   # Инструкция сборки Docker-образа с окружением и зависимостями для запуска тестов
├── docker-compose.yml           # Набор docker-compose сервисов для запуска разных suite (all/smoke/regression/negative)
├── requirements.txt             # Python-зависимости проекта (pytest, requests, allure, pydantic и т.п.)
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

# <p align="center"> 🐳 Локальный запуск тестов (через Docker). </p>

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

После выполнения тестов:

```bash
allure generate allure-results -o allure-report --clean
```

Запустите локальный сервер:

```bash
python -m http.server 8080
```

Откройте в браузере:

```bash
http://localhost:8080
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

1. Перейдите в GitHub → Actions
2. Выберите workflow:

```bash
Test Api Dummy (Manual + Pages + History)
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
