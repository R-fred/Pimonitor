from dataclasses import field as _field
import platform as _pf
import re as _re
import socket as _socket
from typing import Optional as _Optional, Dict as _Dict, Any as _Any
import uuid as _uuid

import psutil as _ps
from pydantic.dataclasses import dataclass as _dataclass

from ._utils import _utc_timestamp

@_dataclass
class ContextData:
    """Class representing a set of data providing context for the monitoring data.

    Returns:
        ContextData: [description]
    """
    ip_address: _Optional[str] = None
    mac_address: _Optional[str] = None
    localhostname: _Optional[str] = _field(init=False, default_factory=_pf.node)
    timestamp: float = _field(init=False, repr=True,
                            metadata={"unit": "s",
                            "description": "returned as seconds from 1970.01.01 00:00"})
  
    boot_time: float = _field(init=False, default_factory=_ps.boot_time, repr=True,
                            metadata={"unit": "s",
                            "description": "returned as seconds from 1970.01.01 00:00"})
    
    def __post_init__(self) -> None:
        self._get_network_addresses()

        if self.ip_address == None:
            self._get_ip_address()
        if self.mac_address == None:
            self._get_uuid_mac_address()

        self.timestamp = _utc_timestamp()
        return None


    def _get_ip_address(self) -> None: # not 100% on mac at least.
        """
        Function to get the IP address of the computer.
        The IP address is associated to the primary network interface.
        """
        try:
            s = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
            s.connect(('10.10.10.10', 1))
            self.ip_address = s.getsockname()[0]
        
        except:
            self.ip_address = None
        
        finally:
            s.close()
            return None


    def _get_uuid_mac_address(self) -> None:
        """
        Function for getting the device's MAC address.
        This is NOT the MAC address of the network adapter.
        """
        try:
            self.mac_address = ':'.join(_re.findall('..', '%012x' % _uuid.getnode()))
        except:
            self.mac_address = None
        return None


    def _get_network_addresses(self) -> None:
        try:
            input = {k: v for k, v in _ps.net_if_addrs().items() for x in v if x.family == 2 and x.address != "127.0.0.1"}
            input = {k: [x for x in v if x.family in (2,18)] for k,v in input.items()}
            input = [(k, x.family, x.address) for k, v in input.items() for x in v]
 
            self.ip_address = [y[2] for y in input if y[1] == 2][0]
            self.mac_address = [y[2] for y in input if y[1] == 18][0]
 
        except:
            self.ip_address = None
            self.mac_address = None
        
        finally:
            return None


    def as_dict(self) -> _Dict[str, _Any]:
        self_dict = self.__dict__
        del self_dict["__initialized__"]
        return self_dict
