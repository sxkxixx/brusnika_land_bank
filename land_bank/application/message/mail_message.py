from .imessage import IMessage


class MailMessage(IMessage):
    def __init__(
            self,
            sender: str,
            receiver: str,
            subject: str
    ):
        self.__sender: str = sender
        self.__receiver: str = receiver
        self.__subject: str = subject

    def get_sender(self) -> str:
        return self.__sender

    def get_receiver(self) -> str:
        return self.__receiver

    def get_subject(self) -> str:
        return self.__subject

    def get_formatted_template(self) -> str:
        raise NotImplementedError()
