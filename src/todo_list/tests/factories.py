import datetime

import factory
from settings import PWD_CONTEXT

from todo_list.models import TODOList, User
from todo_list.schemes.request import (
    TODOListRequestScheme,
    UserRegistrationRequestScheme,
)

ADMIN_PASSWORD = 'admin'
NOT_ADMIN_PASSWORD = 'test'


class UserAdminFactory(factory.Factory):
    class Meta:
        model = User

    username = 'admin'
    password = PWD_CONTEXT.hash(ADMIN_PASSWORD)
    telegram = '@admin'
    last_seen = datetime.datetime.now()
    is_superuser = True


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    password = PWD_CONTEXT.hash(NOT_ADMIN_PASSWORD)
    telegram = factory.LazyAttribute(lambda user: f'@{user.username}')
    last_seen = datetime.datetime.now()
    is_superuser = False


class UserRegistrationFactory(factory.Factory):
    class Meta:
        model = UserRegistrationRequestScheme

    username = factory.Faker('user_name')
    password = factory.Faker('password')
    repeat_password = factory.SelfAttribute('password')
    telegram = factory.LazyAttribute(lambda user: f'@{user.username}')


class TODOListCreateFactory(factory.Factory):
    class Meta:
        model = TODOListRequestScheme

    name = factory.Faker('word', locale='ru_RU')


class TODOListFactory(factory.Factory):
    class Meta:
        model = TODOList

    name = factory.Faker('word', locale='ru_RU')
    user = factory.SubFactory(UserFactory)
