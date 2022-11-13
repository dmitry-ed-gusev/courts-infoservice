###############################################################################
#
#   Dockerfile for the Courts Infoservoce Telegram Bot.
#
#   Useful resources:
#       - https://www.docker.com/blog/how-to-dockerize-your-python-applications/
#
#   Docker commands:
#       - image build: [docker build -t <python-imagename> .]
#       - run container from the image: [docker run <python-imagename>]
#
#   Created: Dmitrii Gusev, 10.10.2022
#   Modified: Dmitrii Gusev, 13.11.2022
#
###############################################################################

# source image with the python 3.10
FROM python:3.10

# our application working dir
WORKDIR /app

# add (copy) content of the [dist] folder to the app working directory
#ADD dist/courts.bot-1.0.0.tar.gz /app
COPY dist/courts.bot-1.0.0.tar.gz /app
COPY .env.prod /app

# upgrade pip
RUN pip install --upgrade pip

# install Courts Info Telegram Bot installation (enabling pre-releases --pre - necessary
# for the pythin-telegram-bot)
RUN pip install /app/courts.bot-1.0.0.tar.gz --pre

# execute Courts Info Telegram Bot
CMD ["courtsbot"]

# use this for creating endless-running container
# ENTRYPOINT ["tail", "-f", "/dev/null"]
