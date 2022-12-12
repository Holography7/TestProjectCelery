import os

from passlib.context import CryptContext

PWD_CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')
MONGO_URI = os.environ.get(
    'DB_URI',
    'mongodb://todo:todo_list@localhost:27016/admin',
)
DATABASE = os.environ.get('DATABASE', 'todo_list')
JWT_ACCESS_SECRET_KEY = os.environ.get(
    'JWT_ACCESS_SECRET_KEY',
    '7b56469aa36b99752087095c8493e663289b066b594731839ef0c8bd57ac8a74',
)
JWT_REFRESH_SECRET_KEY = os.environ.get(
    'JWT_REFRESH_SECRET_KEY',
    'b05525b5b5a7a686b35c5381b951d3d46311e7a8a956021d4884eb39f069e06e',
)
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 10080  # 7 days
