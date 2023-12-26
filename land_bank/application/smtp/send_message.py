from email.message import EmailMessage
from infrastructure.settings import SMTPSettings

from application.message import IMessage
import smtplib


class SendMessage:
	def __init__(self, message: IMessage):
		self.__message: IMessage = message

	def send_mail(self) -> None:
		with smtplib.SMTP_SSL(host=SMTPSettings.HOST, port=SMTPSettings.PORT) as server:
			server.login(SMTPSettings.EMAIL, SMTPSettings.PASSWORD)
			message: EmailMessage = self.__get_mime_message()
			server.send_message(
				msg=message
			)

	def __get_mime_message(self) -> EmailMessage:
		message = EmailMessage()
		message['Subject'] = self.__message.get_subject()
		message['From'] = self.__message.get_sender()
		message['To'] = self.__message.get_receiver()
		message.set_content(
			self.__message.get_formatted_template(), subtype='html'
		)
		return message
