from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from typing import Any as _Any, Dict as _Dict, List as _List, Optional as _Optional

class _IRetriever(metaclass=_ABCMeta):
    
    @staticmethod
    @_abstractmethod
    def retrieve(self, last_n: int) -> _Any:
        pass


class FileRetriever(_IRetriever):

    def __init__(self, file_path: _Optional[str]):
        self.file_path = file_path

    def retrieve(self, last_n: int):
        pass

class SQLiteRetriever(_IRetriever):

    def retrieve(self, last_n: int):
        pass

_RETRIEVERS:  _Dict[str, _Any]= {"file": FileRetriever, "sqlite": SQLiteRetriever}
_RETRIEVERTYPES: _List[_Any] = [k.lower() for k, v in _RETRIEVERS.items()]


class SenderFactory:
    
    @staticmethod
    def build(retriever_type: str, *args, **kwargs) -> _Optional[_IRetriever]:
        output = None
        try:
            if retriever_type.lower() in _RETRIEVERTYPES:
                if len(args) > 0 or len(kwargs) > 0:
                    output = _RETRIEVERS[retriever_type.lower()]
                    output = output(*args, **kwargs)
                else:
                    output = _RETRIEVERS[retriever_type.lower()]
                    output = output()
        except:
            raise
        finally:
            return output