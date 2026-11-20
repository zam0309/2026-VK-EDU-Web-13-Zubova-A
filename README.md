# AskPupkin. ДЗ 3

В этой работе подключила PostgreSQL. Вопросы, ответы, теги и оценки хранятся в базе. Формы пока только для примера.

## Как запустить

Для локального запуска нужны Python 3.13 и PostgreSQL. Создай в PostgreSQL пользователя `askpupkin` и базу `askpupkin` с этим владельцем. Сделай копию `.env.example` с именем `.env.local`. Впиши туда пароль от базы и свой `SECRET_KEY`.

В терминале PyCharm с активным окружением `venv` выполни:

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Если окружения ещё нет, создай его в PyCharm на Python 3.13 или командой `python -m venv venv`. В Windows его можно активировать командой `.\venv\Scripts\Activate.ps1`, в Linux и macOS командой `source venv/bin/activate`.

## Через Docker

Скопируй `.env.example` в `.env.docker`. Поставь `DB_HOST=db`, укажи `SECRET_KEY` и пароль для PostgreSQL. База поднимется вместе с сайтом, миграции применятся при запуске.

```bash
docker compose up --build
```

## Данные и админка

```bash
python manage.py fill_db 20
python manage.py createsuperuser
```

При запуске через Docker добавь перед каждой командой `docker compose exec web`. Для проверки на полном объёме используй `fill_db 10001`. Команда добавляет записи к тем, что уже есть. Минимальное значение `ratio` равно 2.

Сайт открывается на [localhost:8000](http://localhost:8000/), а админка на [localhost:8000/admin/](http://localhost:8000/admin/). Панель Django Debug Toolbar доступна при `DEBUG=True`.

## Страницы

* `/` (новые вопросы)
* `/hot/` (популярные вопросы)
* `/tag/<tag>/` (вопросы по тегу)
* `/question/<id>/` (вопрос с ответами)
* `/ask/` (новый вопрос)
* `/login/` (вход)
* `/signup/` (регистрация)
* `/profile/` (настройки профиля)
