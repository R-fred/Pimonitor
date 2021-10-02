# Product
# Builder interface
# Builder
# Director

from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from collections import deque as _deque
from typing import Dict as _Dict, List as _List, Any as _Any, Optional as _Optional, Deque as _Deque

from ._monitorABC import IMonitor as _IMonitor
from .senders import _ISender as _ISender
from .contextdata import ContextData as _ContextData


class Agent():

    def __init__(self, on_change: bool = True, interval: _Optional[int] = 5) -> None:
        self.context_data: _ContextData = _ContextData()

        self.monitors: _List[_IMonitor] = []
        self.senders: _List[_ISender] = []

        self.interval = interval
        self.on_change = on_change

        self._valuestore: _Deque = _deque(maxlen=300) # Store monitor values
        self._changed: bool = False
    
    def run(self):
        output = None
        try:
            self.monitors = [m() for m in self.monitors]
            self._valuestore.append([m.run() for m in self.monitors])

            if self.on_change and len(self._valuestore) > 1:
                if self._compare_monitoring_values():
                    output = {"context_data": self.context_data.as_dict(),
                            "monitoring_data": [m.as_dict() for m in self.monitors]}
                    for s in self.senders:
                        s.send(message=output)
            else:
                output = {"context_data": self.context_data.as_dict(),
                          "monitoring_data": {m.mtype:m.as_dict() for m in self.monitors}
                          }

        except:
            raise

        finally:
            self._discard_monitoring_data()
            return output
    
    # EXPLAIN: Functions needed to manage the agent's "memory".
    def _compare_monitoring_values(self) -> _Optional[bool]:
        # compare hashes? would need to create a custon hash function for each dataclass.
        output = None
        try:
            if len(self._valuestore) > 1:
                current_item: int = len(self._valuestore)
                previous_item: int = current_item - 1

                current = self._valuestore[current_item]
                previous = self._valuestore[previous_item]

            if len(current) == len(previous):
                check: _List[bool] = [_ == previous[current.index(_)] for _ in current]
                output = all(check)
        except:
            raise
        finally:
            return output

    def _discard_monitoring_data(self) -> None:
        # if the length of self._valuestore reaches its maximum value, discard all values except last entry.
        if len(self._valuestore) == self._valuestore.maxlen:
            self._valuestore = _deque(self._valuestore.pop())

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


# class DAgent:
    
#     def __init__(self) -> None:
#         self._builder: Optional[IAgentBuilder] = None

#     @property
#     def builder(self) -> IAgentBuilder:
#         return self._builder

#     @builder.setter
#     def builder(self, builder: IAgentBuilder) -> None:
#         self._builder = builder


#     @staticmethod
#     def construct(self) -> Agent:
#         self._builder.build_sender()
#         self._builder.build_monitor()

#         return self._builder.build()
