from .mail_message import MailMessage


class PasswordResetMessage(MailMessage):
	TEMPLATE = """
	<!DOCTYPE html>
	<html lang="en">
	<head><meta charset="UTF-8"><title></title></head>
	<body><div>Привет {user_email}</div></body>
	</html>
	"""

	def __init__(self, sender: str, receiver: str, **kwargs):
		super().__init__(
			sender=sender,
			receiver=receiver,
			subject='Смена пароля',
		)
		self.__format_options: dict = kwargs

	def get_formatted_template(self) -> str:
		return self.TEMPLATE.format(**self.__format_options)
