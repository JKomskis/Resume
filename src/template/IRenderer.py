from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path


class IRenderer(ABC):
    @abstractmethod
    def render(self, template_file: Path, data: Any) -> str:
        pass
