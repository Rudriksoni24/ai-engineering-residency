from abc import ABC, abstractmethod

from rag.contracts.document import Document


class BaseLoader(ABC):

    @abstractmethod
    def load(self) -> Document:
        pass