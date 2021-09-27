from fastapi import FastAPI
from pydantic import BaseModel

'''
each end point is named after system name (e.g. edge-100001) followed by the specific monitor
e.g. /edge-100001/cpu, /edge-100001/filesystem, /edge-100001/basic, /edge-100001/advanced
'''