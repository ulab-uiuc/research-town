class OutputFormatError(Exception):
    def __init__(self, message: str = 'Output format error') -> None:
        self.message = message
        super().__init__(self.message)
