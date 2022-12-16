import os

broker_url = os.environ.get('BROKER_URI', 'redis://localhost:6379/0')

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Moscow'
enable_utc = True
task_annotations = {
    'tasks.send_message_about_deleting': {'rate_limit': '60/m'},
}
include = ['celery_app.tasks']
