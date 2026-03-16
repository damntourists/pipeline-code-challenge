from abc import ABC, abstractmethod
from typing import Any

class BaseValidator(ABC):
    @abstractmethod
    def validate(self, data: Any) -> None:
        pass