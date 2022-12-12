import datetime

import factory
from settings import PWD_CONTEXT

from todo_list.models import User
from todo_list.schemes.request import UserRegistrationRequestScheme

ADMIN_PASSWORD = 'admin'


class UserAdminFactory(factory.Factory):
    class Meta:
        model = User

    username = 'admin'
    password = PWD_CONTEXT.hash(ADMIN_PASSWORD)
    telegram = '@admin'
    last_seen = datetime.datetime.now()
    is_superuser = True


class UserRegistrationFactory(factory.Factory):
    class Meta:
        model = UserRegistrationRequestScheme

    username = factory.Faker('user_name')
    password = factory.Faker('password')
    repeat_password = factory.SelfAttribute('password')
    telegram = factory.LazyAttribute(lambda user: f'@{user.username}')
