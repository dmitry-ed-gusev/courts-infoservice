# Courts Info Service :: Telegram Bot

[Project's README.md](../README.md)
[Project's TODO.md](../TODO.md)

## Useful Tech Resources

- [???](???)
- [???](???)

## Building and Running Telegram Bot

### Bot Tech Description

TBD

### Bot directory content

TBD

### Bot build scripts

- [_build_bot.sh](_build_bot.sh) - building bot distribution TAR GZ package in the /dist folder.
- [_build_docker_image.sh](_build_docker_image.sh) - building the docker image (local) for the bot. You should have locally installed Docker (Docker CLI).

### Bot run scripts / commands

In order to run bot, you need to do (depending on the run case/environemnt):

- **LOCAL RUN (DEV)** - you can directly run python file [telegram_bot.py](src/courts/bot/telegram_bot.py)
- **CMD LINE RUN (DEV/LOCAL)** - telegram bot is integrated with the cmd line tools and can be run directly by the command  
  `courtsbot`  
  see the [setup.cfg](setup.cfg) file - section [options.entry_points]
- **RUN BOT IN A CONTAINER (DEV/PROD)** - before container run it worth to build bot docker image and run container via docker compose file [docker-compose.yml](docker-compose.yml) using commands:  
  `docker compose up -d` or `docker compose up --detach`
  The mentioned commands runs container in the detached mode (in background). In case you need to build image before container start - add option **--build** to the commands above:  
  `docker compose up -d --build` or `docker compose up --detach --build`  
  For the Docker Compose execution the standard docker compose file name will be used: **docker-compose.yml**

#### Bot in a Docker container - useful commands

Here are some useful commands for managing bot in a docker container

- `docker logs <container_name> --follow` - attach the current terminal to the logs output (stdout) of the specified <container_name>
- `docker exec -it <container_name> /bin/bash` - get bash shell into the **running** <container_name>
- `docker exec -it <container_name> <command>` - in general execute <command> in the running <container_name>
