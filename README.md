# ДЗ2 проект на Django

## Запуск локально

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

На Linux/macOS вместо второй строки: `source venv/bin/activate`

Сайт: http://127.0.0.1:8000/

## Запуск через Docker

```
docker compose up --build
```

Сайт: http://localhost:8000/

## Страницы

- `/` - новые вопросы
- `/hot/` - популярные вопросы
- `/tag/<tag>/` - вопросы по тегу
- `/question/<id>/` - вопрос с ответами
- `/ask/` - новый вопрос
- `/login/` - вход
- `/signup/` - регистрация
- `/profile/` - настройки профиля
