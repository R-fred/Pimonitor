# Product
# Builder interface
# Builder
# Director

from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from typing import Dict as _Dict, List as _List, Any as _Any, Optional as _Optional

from ._monitorABC import IMonitor as _IMonitor
from .senders import _ISender as _ISender
from .contextdata import ContextData as _ContextData


class Agent():

    def __init__(self) -> None:
        self.context_data: _ContextData = _ContextData()
        self.monitors: _List[_IMonitor] = []
        self.senders: _List[_ISender] = []
    
    def run(self):
        self.monitors = [m() for m in self.monitors]
        monitors = {m.mtype:m.run() for m in self.monitors}

        return {"context_data": self.context_data, "monitors": monitors, "senders": self.senders}

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
