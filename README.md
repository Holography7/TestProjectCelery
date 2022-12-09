# Just my first test project with Celery

I just want to lear use Celery, nothing else.

## Stack realized technologies:

- [X] Python 3.10 (but docker using 3.11)
- [X] FastAPI
- [X] fastapi-health library
- [X] MongoDB
- [X] ODMantic
- [X] pydantic
- [X] passlib
- [X] uvicorn
- [X] jose (JWT)
- [X] Docker
- [X] pre-commit hooks:
   - [X] isort
   - [X] mypy
   - [X] flake8
- [ ] pytest
- [ ] Celery
- [ ] Redis (or RabbitMQ)

## What's this?

It's API that allows creating TODO lists for each user. All data stores in MongoDB.

## Features

- [X] Simple registration users (unfortunately, FastAPI Users not allows ODMantic as backend)
- [X] JWT Authorization
- [ ] Creating TODO List. User have access only to own lists.
- [ ] Superuser can watch all TODO lists
- [ ] Superuser can delete others TODO lists
- [ ] After deleting, every user get on [abstract] telegram message about deleting TODO list (there should work Celery)

## Are you sure that you want try to run it? Then:

- clone this repo
- make sure that you have Docker engine and you able to run docker-compose
- create your own venv in root directory of downloaded repo:

```bash
python3 -m venv venv
```

- create `.env` file in root directory of downloaded repo and type your variables:

| Variable      | Description                          | Recommended value                                       |
|---------------|--------------------------------------|---------------------------------------------------------|
| HOST          | Host of running project in container | 0.0.0.0                                                 |
| PORT          | Port of running project in container | 8000                                                    |
| DB_URI        | URI for connecting to MongoDB        | mongodb://[your user]:[your password]@mongo:27017/admin |
| DATABASE_NAME | Database name in MongoDB             | Any                                                     |
| DB_USER       | User of MongoDB                      | Any                                                     |
| DB_PASS       | Password of User of MongoDB          | Any                                                     |
| DB_NAME       | Database name in MongoDB             | Any                                                     |

- Then just run this project by single command:
```bash
docker-compose up --build
```

This will automatically build project and database images.

If you using MongoDB from this project, your data will save in `celery_mongo-data` (or `[your_dir]_mongo-data`).

## Or maybe you want to fork and develop by itself?

Remember that in this project includes some pre-commit hooks. You can also install it:
```bash
cd dev_tools/pre-commit
pip install -r requirements.txt
pre-commit install
```

Also `dev_tools` contains dockerized MongoDB in `mongo_docker`, so you don't need to install it on local machine. To use it:

- Create `.env` file in `dev_tools/mongo_docker`:

| Variable | Description                                                           | Recommended value |
|----------|-----------------------------------------------------------------------|-------------------|
| DB_USER  | User of MongoDB                                                       | Any               |
| DB_PASS  | Password of User of MongoDB                                           | Any               |
| DB_NAME  | Database name in MongoDB                                              | Any               |
| DB_PORT  | Port that will exposed on your local machine to get access to MongoDB | Any free          |

And run:

```bash
docker-compose up --build
```

Your data will save in `mongo_docker_mongo-data`.