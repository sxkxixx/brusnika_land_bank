from abc import ABC, abstractmethod


class BaseRepository(ABC):
    @abstractmethod
    def create_record(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def get_record(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def select_records(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def update_record(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def get_record_with_relationships(self, *args, **kwargs):
        raise NotImplementedError()
