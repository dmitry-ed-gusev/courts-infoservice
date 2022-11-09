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
#   Modified: Dmitrii Gusev, 10.11.2022
#
###############################################################################

FROM python:3.10
ADD dist/courts.bot-1.0.0a0.tar.gz
RUN pip install requests beautifulsoup4 python-dotenv
CMD [“python”, “./main.py”]
