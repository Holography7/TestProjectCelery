# Just my first test project with Celery

[![build](https://github.com/Holography7/TestProjectCelery/actions/workflows/python-app.yml/badge.svg)](https://github.com/Holography7/TestProjectCelery/actions)

I just want to lear use Celery, nothing else.

## Stack realized technologies:

- [X] Python 3.11
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
   - [X] pytest
- [ ] Celery
- [ ] Redis (or RabbitMQ)

## What's this?

It's API that allows creating TODO lists for each user. All data stores in MongoDB.

## Features

- [X] Simple registration users (unfortunately, FastAPI Users not allows ODMantic as backend)
- [X] JWT Authorization
- [X] Creating TODO List. User have access only to own lists.
- [X] Superuser can watch all TODO lists
- [X] Superuser can delete others TODO lists
- [ ] After deleting, every user get on [abstract] telegram message about deleting TODO list (there should work Celery)

## Are you sure that you want try to run it? Then:

- clone this repo
- make sure that you have Docker engine and you able to run docker-compose
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

If you using MongoDB from this project, your data will save in `[your_dir]_mongo-data`.

To make sure that all works, you can run tests:
```bash
docker ps
docker exec [container_name] pytest
```

## Or maybe you want to fork and develop by itself?

Then create your own venv in root directory of downloaded repo:

```bash
python3 -m venv venv
```

Remember that in this project includes some pre-commit hooks. You can also install it:
```bash
cd dev_tools/pre-commit
pip install -r requirements.txt
pre-commit install
```

Also `dev_tools` contains dockerized MongoDB in `mongo_docker`, so you don't need to install it on local machine. To use it, create `.env` file in `dev_tools/mongo_docker`:

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

Also you can run tests manually from `src` directory:
```bash
pytest
```

Or using coverage:
```bash
coverage run -m pytest
coverage report -m
```

Last coverage report results:

| Name                            | Stmts | Miss | Cover | Missing                         |
|---------------------------------|-------|------|-------|---------------------------------|
| database.py                     | 5     | 0    | 100%  |                                 |
| dependencies.py                 | 6     | 2    | 67%   | 8-9                             |
| main.py                         | 12    | 1    | 92%   | 16                              |
| settings.py                     | 10    | 0    | 100%  |                                 |
| todo_list/__init__.py           | 0     | 0    | 100%  |                                 |
| todo_list/dependencies.py       | 33    | 4    | 88%   | 30-31, 34, 37                   |
| todo_list/enums.py              | 4     | 0    | 100%  |                                 |
| todo_list/flake8_fastapi_fix.py | 2     | 0    | 100%  |                                 |
| todo_list/handlers.py           | 8     | 1    | 88%   | 14                              |
| todo_list/models.py             | 28    | 2    | 93%   | 28, 43                          |
| todo_list/routers.py            | 78    | 8    | 90%   | 49, 52, 72-73, 76, 79, 101, 170 |
| todo_list/schemes/__init__.py   | 0     | 0    | 100%  |                                 |
| todo_list/schemes/request.py    | 23    | 2    | 91%   | 13, 19                          |
| todo_list/schemes/response.py   | 11    | 0    | 100%  |                                 |
| todo_list/tests/__init__.py     | 0     | 0    | 100%  |                                 |
| todo_list/tests/conftest.py     | 71    | 1    | 99%   | 91                              |
| todo_list/tests/factories.py    | 39    | 0    | 100%  |                                 |
| todo_list/tests/tests.py        | 183   | 0    | 100%  |                                 |
| todo_list/utils.py              | 26    | 2    | 92%   | 25-26                           |
| TOTAL                           | 539   | 23   | 96%   |                                 |
