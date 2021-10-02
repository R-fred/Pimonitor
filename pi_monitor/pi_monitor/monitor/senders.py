from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
import datetime as _dt
import time as _time
from typing import Dict as _Dict, List as _List, Any as _Any, Optional as _Optional
from io import BytesIO as _BytesIO
from uuid import uuid4 as _uuid4

from fastapi import FastAPI as _FastAPI
import uvicorn as _uvicorn
import zmq as _zmq


class _ISender(metaclass=_ABCMeta):

    def __init__(self):
        self.id: str = str(_uuid4())

    @staticmethod
    @_abstractmethod
    def send(self):
        pass


class RESTSender(_ISender):# have REST API running separately and POST to the API, GET collects the information from POST

    def __init__(self):
        super().__init__()
    
    def send(self, url: str = "localhost", port: int = 8000, message: str = "REST sender"):
        return f"Message sent on {url}:{port}. Message: {message}. Date and time: {str(_dt.datetime.now())}"


class PubSubSender(_ISender):

    def __init__(self):
        super().__init__()
    
    def send(self):
        return "PubSubSender"


class FileSender(_ISender):
    
    def __init__(self):
        super().__init__()

    def send(self, filepath: str, message: _Any, append: bool = True):
        try:
            fmode = "a"
            if append != True:
                ...

            msg = f"Message sent to {filepath}. Message: {message}. Date and time: {str(_dt.datetime.now())}"

            with open(file = filepath, mode = fmode) as f:
                f.write(msg)
        except:
            raise
        finally:
            return msg


class SQLiteSender(_ISender):

    def __init__(self):
        super().__init__()
    
    def send(self, database_name: str, message: str):
        return f"Message sent to {database_name}. Message: {message}. Date and time: {str(_dt.datetime.now())}"


class StdoutSender(_ISender):

    def __init__(self):
        super().__init__()
    
    def send(self, message: str = f"Message sent to stdout. Message: 'This is a message'. Date and time: {str(_dt.datetime.now())}") -> None:
        print(message)

_SENDERS:  _Dict[str, _Any]= {"rest": RESTSender, "pubsub": PubSubSender, "stdout": StdoutSender, "file": FileSender, "sqlite": SQLiteSender}
_SENDERTYPES: _List[_Any] = [k.lower() for k, v in _SENDERS.items()]

class SenderFactory:
    
    @staticmethod
    def build(sender_type: str = "File") -> _Optional[_ISender]:
        output = None
        try:
            if sender_type.lower() in _SENDERTYPES:
                output = _SENDERS[sender_type.lower()]()
        except:
            raise
        finally:
            return output


# new_sender = SenderFactory().build("SQlite")
# print(new_sender.send("new_db.sqlite", "This is a message being written to an sqlite db"))
# print(new_sender.id)

# new_sender = SenderFactory().build("File")
# print(new_sender.send("~/log.txt", "This is a message being written to a file"))
# print(new_sender.id)