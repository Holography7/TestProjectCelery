import json
import socket

from celery_app.celery import app
from celery_app.settings import (
    ABSTRACT_TELEGRAM_HOST,
    ABSTRACT_TELEGRAM_PORT,
    ABSTRACT_TELEGRAM_SUCCESS_RESPONSE,
    MESSAGE_TEMPLATE,
)


@app.task(name='send_message_about_deleting')
def send_message_about_deleting(
        username: str,
        name_deleted_todo_list: str,
        telegram: str,
) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as abs_telegram:
        abs_telegram.connect((ABSTRACT_TELEGRAM_HOST, ABSTRACT_TELEGRAM_PORT))
        abs_telegram.sendall(
            json.dumps(
                {
                    'telegram': telegram,
                    'message': MESSAGE_TEMPLATE.format(
                        username=username,
                        todo_list_name=name_deleted_todo_list,
                    ),
                },
            ).encode('utf8'),
        )
        data = abs_telegram.recv(1024)
    response = json.loads(data.decode('utf8'))
    if response != ABSTRACT_TELEGRAM_SUCCESS_RESPONSE:
        raise ValueError(
            f'From telegram got unsuccessful response: {response}',
        )
