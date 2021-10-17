# Product
# Builder interface
# Builder
# Director

from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from collections import deque as _deque
import datetime as _dt
import json as _json
from threading import Thread as _Thread, Event as _Event
from time import sleep as _sleep
from typing import Dict as _Dict, List as _List, Any as _Any, Optional as _Optional, Deque as _Deque, Union as _Union

from rich.console import Console as _Console

from ._monitorABC import IMonitor as _IMonitor
from .senders import _ISender as _ISender
from .contextdata import ContextData as _ContextData


class Agent(_Thread):

    def __init__(self, interval: _Optional[_Union[int, float]] = 5, queue_length: int = 15, reload_context_every: _Optional[float] = None) -> None:

        # Removed on_change functionality:
        # on init: on_change: bool = True,
        # attributes: self.on_change = on_change, self._changed: bool = False

        super().__init__()

        self.context_data: _ContextData = _ContextData()
        self.reload_context_every = reload_context_every

        self.monitors: _List[_IMonitor] = []
        self.senders: _List[_ISender] = []

        self.interval = interval
        self.queue_length = queue_length

        self._valuestore: _Deque = _deque(maxlen=self.queue_length) # Store monitor values - was originally added to support on_change functionality.
        self.event: _Event = _Event()
    
    def run(self):
        output = None

        console = _Console()

        try:
            while not self.event.is_set():
                if self.reload_context_every != None:
                    if _dt.datetime.now().timestamp() >= (self.context_data.timestamp + self._contextdata_reload):
                        self.context_data = _ContextData()
                
                initial = [m() for m in self.monitors if m.was_run == False]
                if len(initial) > 0:
                    self.monitors = initial
                
                self._valuestore.append([m.run() for m in self.monitors])

                if len(self._valuestore) >= 1:
                    output = {"context_data": self.context_data.as_dict(),
                              "monitoring_data": {m.mtype: m.as_dict() for m in self._valuestore.pop()}
                             }
                    output = _json.dumps(output)
                
                if len(self.senders) > 0:
                    for s in self.senders:
                        s.send(message=output)
                
                _sleep(self.interval)

        except KeyboardInterrupt:
            if not self.event.is_set():
                self.event.set()
            console.print("\n> Execution stopped by user\n", style="red")       

        except:
            if not self.event.is_set():
                self.event.set()
            console.print("\nError\n")

        finally:
            if not self.event.is_set():
                self.event.set()
                self.join(timeout=5)
            return None
    
    # EXPLAIN: Functions needed to manage the agent's "memory".
    # def _compare_monitoring_values(self) -> bool:
    #     # compare hashes? would need to create a custon hash function for each dataclass.
    #     output = False
    #     try:
    #         if len(self._valuestore) > 1:
    #             current_item: int = len(self._valuestore)
    #             previous_item: int = current_item - 1

    #             current = self._valuestore[current_item]
    #             previous = self._valuestore[previous_item]

    #         if len(current) == len(previous):
    #             check: _List[bool] = [_ == previous[current.index(_)] for _ in current]
    #             output = all(check)
    #     except:
    #         raise
    #     finally:
    #         return output


    def list_parts(self) -> _Dict[str, _List[_Any]]:
        return {"monitors": self.monitors, "senders": self.senders}


class _IAgentBuilder(metaclass=_ABCMeta):

    @staticmethod
    @_abstractmethod
    def add_sender():
        pass
    
    @staticmethod
    @_abstractmethod
    def add_monitor():
        pass  

    @staticmethod
    @_abstractmethod
    def build():
        pass


class AgentBuilder(_IAgentBuilder):

    def __init__(self) -> None:
        self.reset()
    
    def reset(self) -> None:
        self._product: Agent = Agent()

    def add_sender(self, sender: _Any) -> None:
        self._product.senders.append(sender)
    
    def add_monitor(self, monitor: _IMonitor) -> None:
        self._product.monitors.append(monitor)
    
    def build(self) -> Agent:
        product = self._product
        self.reset()
        return product


# from pi_monitor.monitor.singleMonitors import CPU, Uptime, Memory, Disk, Process


# ag_builder = AgentBuilder()
# ag_builder.add_monitor(Uptime)
# ag_builder.add_monitor(CPU)
# ag_builder.add_monitor(Memory)
# ag_builder.add_monitor(Disk)
# ag_builder.add_monitor(Process)
# agent = ag_builder.build()

# agent.run()