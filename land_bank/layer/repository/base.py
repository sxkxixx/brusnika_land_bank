from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository(ABC):
    @abstractmethod
    def __init__(self, session: 'AsyncSession'):
        raise NotImplementedError()

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

    @abstractmethod
    def get_or_create_record(self, *args, **kwargs):
        raise NotImplementedError()
