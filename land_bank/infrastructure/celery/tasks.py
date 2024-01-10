from application.message import IMessage
from application.smtp import SendMessage
from .client import celery_client

__all__ = [
    'send_message'
]


@celery_client.task()
def send_message(message: 'IMessage') -> None:
    sender = SendMessage(message)
    sender.send_mail()
