#  ДЗ 1 (статическая верстка)

## Как открыть
Откройте файл `public/index.html` в браузере

можно запустить локальный сервер:

```bash
cd public
python3 -m http.server 8000
```
затем откройте http://localhost:8000/index.html.

## Страницы

| Страница | Файл | Содержание |
|---|---|---|
| base | `public/base.html` | общий layout: header, main, sidebar, footer |
| index | `public/index.html` | список новых вопросов с пагинацией |
| hot | `public/hot.html` | список популярных вопросов |
| tag | `public/tag.html` | вопросы по тегу |
| question | `public/question.html` | вопрос, ответы, пагинация ответов, форма ответа |
| ask | `public/ask.html` | форма нового вопроса |
| login | `public/login.html` | форма входа |
| signup | `public/signup.html` | форма регистрации |
| profile | `public/profile.html` | настройки профиля (шапка в состоянии «авторизован») |