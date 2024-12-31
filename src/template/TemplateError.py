class TemplateError(Exception):
    """Raised when there is an error rendering a template"""

    def __init__(self, message: str = "") -> None:
        super().__init__(message)

    @property
    def message(self) -> str:
        return self.message
