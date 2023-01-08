# How to create mysql db

Start mysql docker
```
docker run -it -m 8G --cpus=2 --name courts-info-dev \
--env=MYSQL_ROOT_PASSWORD=<pwd> -p 33061:3306 --restart=unless-stopped -d mysql:latest 
```

Config file - my.cnf. After copying it into docker container (/etc/my.cnf) restart the container.

Connect to db with root/<pwd> creds and create etl user:

```
create user usr_etl identified by '<password>';

GRANT ALL PRIVILEGES ON * . * TO usr_etl;
```

Set binary logs expire timeout, increase connections limit to 300 and set MSK timezone:
```
SET PERSIST binlog_expire_logs_seconds = 3600;

SET PERSIST max_connections = 300;

SET PERSIST time_zone = '+3:00';
```

Then import mysql backup or execute all sql scripts from sql/mysql folder.

