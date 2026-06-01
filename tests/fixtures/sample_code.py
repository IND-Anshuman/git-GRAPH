SAMPLE_PYTHON_MODULE = """
import logging
from typing import List

MAX_RETRIES = 3
logger = logging.getLogger(__name__)

class BaseService:
    def __init__(self):
        self.initialized = True

class MyService(BaseService):
    def process(self, data: List[str]) -> bool:
        if not data:
            return False
        return self._do_process(data)
        
    def _do_process(self, data):
        logger.info("Processing")
        return True

def standalone_function():
    svc = MyService()
    svc.process(["test"])
"""

SAMPLE_SIMPLE_FUNCTION = """
def hello(name: str) -> str:
    return f'Hello {name}'
"""

SAMPLE_CLASS = """
class DataModel:
    def __init__(self, id):
        self.id = id
        
    @property
    def identity(self):
        return self.id
"""

SAMPLE_IMPORTS = """
import os
from sys import path
import json as jsn
"""
