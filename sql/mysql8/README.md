# How to create mysql db

Start mysql docker
```
docker run -it -m 8G --name courts-info-dev --env=MYSQL_PASSWORD=dev --env=MYSQL_DATABASE=courts_info \
--env=MYSQL_ROOT_PASSWORD=<pwd> --env=MYSQL_USER=dev -p 33061:3306 --restart=unless-stopped -d mysql:latest 
```

Connect to db with root/<pwd> creds and create etl user:

```
create user usr_etl identified by '<password>';

GRANT ALL PRIVILEGES ON * . * TO usr_etl;
```

Set binary logs expire timeout:
```
SET GLOBAL binlog_expire_logs_seconds = 3600
```

Then import mysql backup or execute all sql scripts from this folder.

