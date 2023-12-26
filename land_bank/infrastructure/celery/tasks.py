from application.message import IMessage
from .client import celery_client
from application.smtp import SendMessage

__all__ = [
	'send_message'
]


@celery_client.task()
def send_message(message: 'IMessage') -> None:
	sender = SendMessage(message)
	sender.send_mail()
