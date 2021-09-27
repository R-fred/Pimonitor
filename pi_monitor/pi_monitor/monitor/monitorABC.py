from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from .utils import _uuid, get_monitor_name

# from pydantic.dataclasses import dataclass


@dataclass
class IMonitor(metaclass=ABCMeta):
    """Abstract interface class for all monitors.

    Args:
        metaclass ([type], optional): [description]. Defaults to ABCMeta.
    """

    id: str = field(init=False, default_factory=_uuid, repr=True)
    mtype: Optional[str] = field(init=False, default="IMonitor")
    timestamp: float = field(init=False, default=None,repr=True,
                            metadata={"unit": "s",
                            "description": "returned as seconds from 1970.01.01 00:00"})
    was_run: bool = field(init=False, default=False, repr=False)

    @staticmethod
    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def as_dict(self) -> Dict[str, Any]:
        pass