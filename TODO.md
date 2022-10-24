# TODO for the project

Список задач - что надо сделать в проекте :)))

Основная документация проекта: [README.md](README.md)

## General Improvements

1. ~~General: load_dotenv - в боте пароль попадает прямо в лог. надо сделать маскирование, как для токена~~
2. General: init db питон скрипт. список скриптов в db_init_config.py. в db_tools уже есть метод для этого, 
   можно туда положить

## Database Improvements

1. DB: неодходим спец префикс для таблиц скрапера в БД - они перемешиваются с таблицами Джанги
2. ???

## Scraper Improvements

1. Scraper: implement execution as a standalone application (from shell/cmd line) - not from the pycharm
2. ???

## Web UI Improvements

1. ~~Web UI: добавить поле stage (courts table)~~
2. ~~Web UI: убрать ID со страницы + убрать алиас суда~~
3. Web UI: кнопка на сайте добавляющая подписку в боте (!!!)
4. Web UI: статистика - новое поле - дата обновления
5. Web UI: add build/deployment script(s) - automation
6. Web UI: switch to the latest version of Bootstrap Framework (5.2 - ?)
7. Web UI: proper serving of the static files
8. ~~Web UI: initially show the empty screen with the search form - once search performed - show results~~
9. Make links from [Statistics] page to the courts details page

## Telegram Bot Improvements

1. TeleBot: dockerize (create docker file for the bot)
2. TeleBot: сделать sh/exe для запуска бота просто из консоли, чтобы pycharm не жрал ресурсы
3. TeleBot: deployment to the k8s/microk8s (see: https://microk8s.io/)
