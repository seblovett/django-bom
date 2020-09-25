# pull official base image
FROM ubuntu:18.04

# set work directory
WORKDIR /usr/src/app
EXPOSE 8000
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update \
    && apt-get install -y gcc python3-dev musl-dev libffi-dev libmysqlclient-dev python3-pip
# install dependencies
RUN python3 -m pip install --upgrade pip
COPY ./requirements.txt .
RUN python3 -m pip install -r requirements.txt


# copy project
COPY . .

# run entrypoint.sh
# ENTRYPOINT ["ls"] 
# /usr/src/app/entrypoint.sh"]
ENTRYPOINT ["python3", "manage.py","runserver", "0.0.0.0:8000"]
