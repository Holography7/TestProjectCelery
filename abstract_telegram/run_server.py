import json
import logging
import logging.config
import os
import signal
import socket
from typing import Any

dict_config = {
    'version': 1,
    'formatters': {
        'simple': {'format': '%(asctime)s [%(levelname)s]: %(message)s'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'telegram': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}

logging.config.dictConfig(dict_config)
logger = logging.getLogger('telegram')

HOST = os.environ.get('ABSTRACT_TELEGRAM_HOST', '127.0.0.1')
PORT = int(os.environ.get('ABSTRACT_TELEGRAM_PORT', '65432'))


class GracefulKiller:
    kill_now = False

    def __init__(self) -> None:
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args: Any) -> None:
        logger.info('Graceful stopping...')
        self.kill_now = True
        server.close()


if __name__ == '__main__':
    killer = GracefulKiller()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        logger.info('Abstract telegram server start for listening')
        server.bind((HOST, PORT))
        while not killer.kill_now:
            server.listen()
            try:
                conn, addr = server.accept()
            except OSError:
                pass
            else:
                with conn:
                    logger.info(f'Received message from {addr}')
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        decoded_data = json.loads(data.decode('utf8'))
                        telegram = decoded_data['telegram']
                        message = decoded_data['message']
                        logger.info(
                            f'Got message, addressed to {telegram}: {message}',
                        )
                        conn.sendall(
                            json.dumps({'status': 'accepted'}).encode('utf8'),
                        )
