import os
import socket

from celery_app.utils import is_ip_address

ABSTRACT_TELEGRAM_HOST = os.environ.get('ABSTRACT_TELEGRAM_HOST', '127.0.0.1')
if not is_ip_address(ABSTRACT_TELEGRAM_HOST):
    ABSTRACT_TELEGRAM_HOST = socket.gethostbyname(ABSTRACT_TELEGRAM_HOST)
    print(f'ABSTRACT_TELEGRAM_HOST={ABSTRACT_TELEGRAM_HOST}')
ABSTRACT_TELEGRAM_PORT = int(os.environ.get('ABSTRACT_TELEGRAM_PORT', 54321))
MESSAGE_TEMPLATE = (
    'Пользователь {username} посмел создать TODO лист с оскорбительным '
    'названием {todo_list_name}. Мы успешно удалили этот TODO List, а '
    'пользователь {username} получает звание дурака!'
)
ABSTRACT_TELEGRAM_SUCCESS_RESPONSE = {'status': 'accepted'}
