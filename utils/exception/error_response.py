class ErrorResponse:
    def __init__(self, name, status_code,message):
        self.name = name
        self.status_code = status_code
        self.message = message