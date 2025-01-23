from utils.exception.error_response import ErrorResponse
class DataException(Exception):
    def __init__(self, error: ErrorResponse):
        self.message = error.message
        self.status_code = error.status_code
        self.name = error.name
