from fastapi import FastAPI
from fastapi_health import health
from uvicorn import run as uvicorn_run

from todo_list import routers
from todo_list.handlers import add_exception_handlers
from todo_list.utils import check_database

app = FastAPI()

app.include_router(routers.router)
app.add_api_route('/health', health([check_database]))
add_exception_handlers(app)

if __name__ == '__main__':
    uvicorn_run('main:app', port=8060, log_level='info')
