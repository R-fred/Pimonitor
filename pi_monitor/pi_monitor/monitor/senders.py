from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
import datetime as _dt
import time as _time
from typing import Dict as _Dict, List as _List, Any as _Any, Optional as _Optional
from io import BytesIO as _BytesIO
import json as _json
import re as _re
import sqlite3 as _sqlite3
from uuid import uuid4 as _uuid4

# from fastapi import FastAPI as _FastAPI
# import uvicorn as _uvicorn
# import zmq as _zmq


class _ISender(metaclass=_ABCMeta):

    def __init__(self):
        self.id: str = str(_uuid4())

    @staticmethod
    @_abstractmethod
    def send(self, message: _Any):
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
    
    def __init__(self, filepath: str, append: bool = True):
        super().__init__()
        self.file_path = filepath
        self.append = append

    def send(self, message: _Any):
        try:
            fmode = "w"
            if self.append:
                fmode = "a"

            msg = f"\n> {str(_dt.datetime.now())}: {message}."

            with open(file = self.file_path, mode = fmode, newline="\n", encoding="utf-8") as f:
                f.write(msg)
        except:
            raise
        finally:
            return msg


class SQLiteSender(_ISender):

    def __init__(self, database_name: str, table_name: _Optional[str] = None):
        super().__init__()
        self.database_name = database_name
        self.table_name = table_name
    
    def send(self, message: str):
        """[summary]

        Args:
            message (str): [description]
            database_name (str): [description]
            table_name (_Optional[str], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """

        try:
            msg = _json.loads(message)
            data = msg["monitoring_data"]
            ctxt = msg["context_data"]
            if self.table_name == None:
                self.table_name = ctxt['localhost_name']
                self.table_name = self.table_name.replace("-", "_")
                self.table_name = self.table_name.replace(".", "_")

            db_table = f"CREATE TABLE IF NOT EXISTS {self.table_name} (timestamp TEXT, context JSON, monitors TEXT, data json)"

            conn = _sqlite3.connect(database=self.database_name)
            c = conn.cursor()
            
            c.execute(db_table) # create table if it does not exist
            
            stmt = f"INSERT INTO {self.table_name} VALUES ('{str(_dt.datetime.now())}', '{_json.dumps(ctxt)}', '{'; '.join(data.keys())}', '{_json.dumps(data)}')"
            c.execute(stmt)
            conn.commit()
            conn.close()

        except:
            print("----> Error in SQLiteSender <----")
            print(stmt)
            raise


class ConsoleSender(_ISender):

    def __init__(self):
        super().__init__()
    
    def send(self, message: str = f"Message sent to stdout. Message: 'This is a message'. Date and time: {str(_dt.datetime.now())}") -> None:
        print(message)

_SENDERS:  _Dict[str, _Any]= {"rest": RESTSender, "pubsub": PubSubSender, "console": ConsoleSender, "file": FileSender, "sqlite": SQLiteSender}
_SENDERTYPES: _List[_Any] = [k.lower() for k, v in _SENDERS.items()]

class SenderFactory:
    
    @staticmethod
    def build(sender_type: str, **kwargs) -> _Optional[_ISender]:
        try:
            if sender_type.lower() in _SENDERTYPES:
                output = _SENDERS[sender_type.lower()](**kwargs)
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