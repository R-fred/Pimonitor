from abc import ABCMeta as _ABCMeta, ABC as _ABC, abstractmethod as _abstractmethod
import datetime as _dt
from genericpath import exists
import time as _time
from typing import Dict as _Dict, List as _List, Any as _Any, Optional as _Optional, Tuple as _Tuple, Union as _Union
from io import BytesIO as _BytesIO
import json as _json
from os.path import expanduser as _expanduser
import platform as _pf
import re as _re
import sqlite3 as _sqlite3
from uuid import uuid4 as _uuid4

import pika as _pika
from pika import BlockingConnection as _BlockingConnection

# from fastapi import FastAPI as _FastAPI
# import uvicorn as _uvicorn
# import zmq as _zmq


class _ISender(metaclass=_ABCMeta):

    def __init__(self):
        self.id: str = str(_uuid4())
        self.stype: str = "_ISender"

    @staticmethod
    @_abstractmethod
    def send(self, message: _Any):
        pass


# TODO: Implement
class RESTSender(_ISender):# have REST API running separately and POST to the API, GET collects the information from POST

    def __init__(self):
        super().__init__()
        self.stype: str  = "rest_sender"
    
    def send(self, url: str = "localhost", port: int = 8000, message: str = "REST sender"):
        return f"Message sent on {url}:{port}. Message: {message}. Date and time: {str(_dt.datetime.now())}"


class RabbitMQSender(_ISender):

    def __init__(self, queue: str = "default", host: str = "localhost", port: int = 5672, credentials: _Optional[_Tuple[str]] = None, keep_alive: _Union[int, float] = 600):
        super().__init__()
        self.stype: str  = "rabbitmq_sender"
        self.host = host
        self.port = port
        self.credentials = credentials
        self.queue = queue
        
        self.connection: _Optional[_BlockingConnection] = None
        
        try:
            self.connection = self._open_connection()
        except:
            self.connection = None
        
        self.connection_timestamp: _Optional[float] = None
        
        self.keep_alive: _Union[int, float] = keep_alive
    
    
    def send(self, message: _Any) -> None:
        
        try:
            if self.connection.is_closed:
                self.connection = self._create_connection()

            self.connection_timestamp = _dt.datetime.now().timestamp()
            
            channel = self.connection.channel()
            channel.queue_declare(queue=self.queue)
            
            channel.basic_publish(exchange='',
                        routing_key=self.queue,
                        body=message)

            if _dt.datetime.now().timestamp() >= (self.connection_timestamp + self.keep_alive):
                self._close_connection()
        except BaseException as e:
            self._close_connection()
            raise e
        
        finally:
            return None


    def _open_connection(self) -> _Optional[_BlockingConnection]:
        
        connection = None
        
        try:
            try:
                credentials = _pika.PlainCredentials(username=self.credentials[0], password=self.credentials[1])
            except:
                credentials = None
                print(">> credentials failed")
            
            connection = _pika.BlockingConnection(_pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials))
        
        except BaseException as e:
            print(">> Connection failed")
            raise e
        
        finally:
            return connection


    def _close_connection(self) -> None:
        if self.connection.is_open:
            self.connection.close(reply_text="closing RabbitMQ connection...")
        
        return None


# TODO: Implement
class PubSubSender(_ISender):

    def __init__(self):
        super().__init__()
        self.stype: str  = "zeromq_pubsub_sender"
    
    def send(self):
        return "PubSubSender"


class FileSender(_ISender):
    
    def __init__(self, filepath: _Optional[str] = None, append: bool = True):
        super().__init__()
        self.stype: str  = "file_sender"
        self.file_path = filepath

        if self.file_path == None:
            fpath = f'{_expanduser("~")}/{_pf.node()}_monitoring.txt'.replace(":", "-").replace(" ", "_")
            self.file_path = fpath

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

    def __init__(self, databasepath: _Optional[str] = None, table_name: _Optional[str] = None):
        super().__init__()
        self.stype: str  = "sqlite_sender"
        self.database_name = databasepath
        self.table_name = table_name

        node = _pf.node().replace(":", "_").replace(" ", "_").replace(".", "_").replace("-", "_")

        if self.database_name == None or len(databasepath) == 0:
            fpath = f'{_expanduser("~")}/{node}_monitoring.sqlite'
            self.database_name = fpath
        
        if self.table_name == None or len(self.table_name) == 0:
            self.table_name = node

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
            raise


# TODO: Implement.
class ConsoleSender(_ISender):

    def __init__(self):
        super().__init__()
        self.stype: str  = "console_sender"
    
    def send(self, message: str = f"Message sent to stdout. Message: 'This is a message'. Date and time: {str(_dt.datetime.now())}") -> None:
        print(message)


_SENDERS:  _Dict[str, _Any]= {"rest": RESTSender, "pubsub": PubSubSender, "rabbitmq": RabbitMQSender, "console": ConsoleSender, "file": FileSender, "sqlite": SQLiteSender}
_SENDERTYPES: _List[_Any] = [k.lower() for k, v in _SENDERS.items()]


class SenderFactory:
    
    @staticmethod
    def build(sender_type: str, *args, **kwargs) -> _Optional[_ISender]:
        output = None
        try:
            if sender_type.lower() in _SENDERTYPES:
                if len(args) > 0 or len(kwargs) > 0:
                    output = _SENDERS[sender_type.lower()]
                    output = output(*args, **kwargs)
                else:
                    output = _SENDERS[sender_type.lower()]
                    output = output()
        except:
            raise
        finally:
            return output

# new_file_sender = SenderFactory.build("file")
# new_file_sender.send("message")
# print(type(new_file_sender))
# print(new_file_sender.stype)

# new_sender = SenderFactory().build("rabbitmq", credentials=("test", "test"))
# print(type(new_sender))
# new_sender.send(message="message")

# print(new_sender.send(message='{"context_data": {"one":"one"}, "monitoring_data": {"two": "This is a message being written to an sqlite db"}}'))
# print(new_sender.stype)