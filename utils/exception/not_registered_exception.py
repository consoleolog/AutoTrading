from typing import Any

class NotRegisteredException(Exception):
    def __init__(self, type: Any, message:str):
        self.type = type
        self.message = message
