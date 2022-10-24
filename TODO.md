# TODO for the project

Список задач - что надо сделать в проекте :)))

Основная документация проекта: [README.md](README.md)

1. ~~General: load_dotenv - в боте пароль попадает прямо в лог. надо сделать маскирование, как для токена~~
2. General: init db питон скрипт. список скриптов в db_init_config.py. в db_tools уже есть метод для этого,
   можно туда положить
3. TeleBot: сделать sh/exe для запуска бота просто из консоли, чтобы pycharm не жрал ресурсы
4. Scraper: implement execution as a standalone application (from shell/cmd line) - not from the pycharm
5. DB: неодходим спец префикс для таблиц скрапера в БД - они перемешиваются с таблицами Джанги
6. Web UI: добавить поле stage (courts table)
7. Web UI: убрать ID со страницы + алиас суда
8. Web UI: кнопка на сайте добавляющая подписку в боте
9. Web UI: статистика - новое поле - дата обновления
10. Web UI: add build/deployment script(s) - automation
11. TeleBot: dockerize (create docker file for the bot)
12. TeleBot: deployment to the k8s/microk8s (see: https://microk8s.io/)
13. Web UI: switch to the latest version of Bootstrap Framework (5.2 - ?)
14. Web UI: proper serving of the static files
15. ???
