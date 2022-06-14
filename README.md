# Yatube
### Описание
Социальная сеть для публикации личных дневников. Это сайт, на котором можно создать свою страницу. 
Проект создан по MTV архитектуре. Реализованы возможности регистрации и восстановления/ смены пароля через почту, перелистывание страниц, кеширование данных. К проекту написаны тесты, проверяющие работу сервиса
### Технологии
```
Python 3.7
```
```
Django 2.2.19
```
### Запуск проекта в dev-режиме
- Установите и активируйте виртуальное окружение
```
python3 -m venv venv
```

```
source venv/bin/activate
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```

- Выполнить миграции:

```
python3 manage.py migrate
```
- В папке с файлом manage.py выполните команду:
```
python3 manage.py runserver
```
### Авторы

Анжела Намистюк 


[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)
