## Foodgram ("Продуктовый помошник")
---

[![Django-app workflow](https://github.com/antsyganok/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)](https://github.com/antsyganok/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

---
### Описание:
Это сервис на котором авторизованые пользователи могут публиковать свои рецепты, добавлять в избранное рецепты других пользователей, а так же подписываться на авторов рецептов. Авторизованый пользователь так же может добавить рецепты котороые он решил приготовить в корзину, а затем скачать минимально необходимый список продуктов для их приготовления.
Не авторизованые пользователи могут просматривать рецепты других пользователей.

---
[Документация в формате редок][lnk]

[lnk]: http://pyrojoke.ddns.net/api/docs/

---

#### Как запустить проект при помощи Docker:

##### Клонируйте репозиторий:
```sh
git clone git@github.com:antsyganok/foodgram-project-react.git
```
#### Перейдите в директорию \infra и создайте файл ".env" (без ковычек):
##### Шаблон наполнения файла:
```sh
DB_ENGINE=django.db.backends.postgresql # Указываем, что работаем с postgresql
DB_NAME=postgres # Имя базы данных
POSTGRES_USER=postgres # Логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # Пароль для подключения к БД
DB_HOST=db # Название сервиса (контейнера)
DB_PORT=5432 # Порт для подключения к БД
```

### Для запуска приложения в Docker контейнерах перейдите в директорию "\infra" и выполните команды:

Чтобы развернуть докер контэйнеры:
```sh
docker-compose up
```
Чтобы пересобрать докер контейнеры используйте команду:
```sh
docker-compose up -d --build 
```
Чтобы выполнить миграции воспользуйтесь командой:
```sh
docker-compose exec web python manage.py migrate
```
После применения миграций будут импортированы теги и ингредиенты

Если нужно создать суперпользователя выполинте команду:
```sh
docker-compose exec web python manage.py createsuperuser
```
Чтобы собирать статику используем конманду:
```sh
docker-compose exec web python manage.py collectstatic --no-input
```
Чтобы остановить и удалить контейнеры можно использовать команду:
```sh
docker-compose down -v
```
---
#### Как запустить проект локально:
Клонировать репозиторий:
```sh
git clone git@github.com:antsyganok/foodgram-project-react.git
```
Cоздать и активировать виртуальное окружение:
```sh
python3 -m venv venv
source venv/bin/activate
```
Установить зависимости из файла requirements.txt:
```sh
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
Выполнить миграции:
```sh
python3 manage.py migrate
```
Запустить проект:
```sh
python3 manage.py runserver
```

#### Стек:
![python version](https://img.shields.io/badge/Python-3.7.9-gold?style=flat-square&logo=python) ![django version](https://img.shields.io/badge/Django-3.2-purple?style=flat-square&logo=django) ![django version](https://img.shields.io/badge/Django%20REST%20Framework-%203.12.4-purple?style=flat-square&logo=django)
![docker version](https://img.shields.io/badge/Docker-%204.17.0-blue?style=flat-square&logo=docker) ![nginx version](https://img.shields.io/badge/Nginx-%201.21.3-ligtgreen?style=flat-square&logo=nginx) ![gunicorn version](https://img.shields.io/badge/Gunicorn-%2020.0.4-orange?style=flat-square&logo=gunicorn) ![postgres version](https://img.shields.io/badge/PostgreSQL-%202.37.1-darkblue?style=flat-square&logo=postgresql)
![git version](https://img.shields.io/badge/Git-%202.37.1-black?style=flat-square&logo=github) ![yandexcloud version](https://img.shields.io/badge/Yandex_Cloud-%2020.0.4-skyblue?style=flat-square)

##### Разработчик (backend):
* Антон Цыганок
