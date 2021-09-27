from collections import namedtuple
import datetime as dt
import re
from typing import Any
import uuid

FileSizes = namedtuple("Filesizes", ["GB", "MB", "KB", "B"])
UpTimeData = namedtuple(typename="UpTimeData", field_names=("days", "hours","minutes","seconds"))

FILESIZES = FileSizes(GB=1024*1024*1024, MB=1024*1024, KB=1024, B=1)


def _utc_timestamp() -> float:
    """Returns a UTC timestamp

    Returns:
        float: utc timestamp
    """
    ts = dt.datetime.now(tz=dt.timezone.utc)
    return ts.timestamp()


def _uuid() -> str:
    id = uuid.uuid4()
    return str(id)


REGEX = re.compile(pattern="\.[A-Za-z_-]+")


def get_monitor_name(monitor: Any) -> str:
    output = "IMonitor"
    string = str(monitor.__class__)
    try:
        output = re.findall(REGEX, string)[0].strip(".")
    except:
        raise
    finally:
        return output
