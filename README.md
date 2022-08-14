# Foodgram
Сайт Foodgram - «Продуктовый помощник». 
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, 
добавлять понравившиеся рецепты в список «Избранное», 
а перед походом в магазин скачивать сводный список продуктов, 
необходимых для приготовления одного или нескольких выбранных блюд.

#### Пример развернутого проекта можно посмотреть [здесь](http://51.250.31.95/)

## Технологии:
- Python 3.10
- Django 3.2
- Django REST framework 3.13
- Nginx
- Docker
- PostgreSQL

## Запуск и работа с проектом:

1) Клонировать репозиторий GitHub (не забываем создать виртуальное окружение и установить зависимости):
```python
git clone https://github.com/vshkinder/foodgram-project-react
```
3) Создать файл ```.env``` в папке проекта _/infra/_ и заполнить его всеми ключами:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123qwe
DB_HOST=db
DB_PORT=5432
```
3) Собрать контейнеры:
```python
cd foodgram-project-react/infra
docker-compose up -d --build
```
4) Сделать миграции, собрать статику и создать суперпользователя:
```python
sudo docker-compose exec web python manage.py makemigrations users
sudo docker-compose exec web python manage.py makemigrations recipes
sudo docker-compose exec -T web python manage.py migrate --noinput
sudo docker-compose exec -T web python manage.py collectstatic --no-input
```
### <br /> Автор проекта:
Шкиндер Валерий<br />
vshkinder11@yandex.ru
