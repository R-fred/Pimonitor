from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from dataclasses import dataclass as _dataclass, field as _field
from typing import Dict as _Dict, Any as _Any, Optional as _Optional

from ._utils import _uuid

# from pydantic.dataclasses import dataclass


@_dataclass
class IMonitor(metaclass=_ABCMeta):
    """Abstract interface class for all monitors.

    Args:
        metaclass ([type], optional): [description]. Defaults to ABCMeta.
    """

    id: str = _field(init=False, default_factory=_uuid, repr=True)
    mtype: _Optional[str] = _field(init=False, default="IMonitor")
    timestamp: float = _field(init=False, default=None,repr=True,
                            metadata={"unit": "s",
                            "description": "returned as seconds from 1970.01.01 00:00"})
    was_run: bool = _field(init=False, default=False, repr=False)

    @staticmethod
    @_abstractmethod
    def run(self):
        pass

    @_abstractmethod
    def as_dict(self) -> _Dict[str, _Any]:
        pass