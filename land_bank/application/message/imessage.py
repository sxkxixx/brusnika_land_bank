from abc import abstractmethod, ABC


class IMessage(ABC):
    @abstractmethod
    def get_formatted_template(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_sender(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_receiver(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_subject(self) -> str:
        raise NotImplementedError()
