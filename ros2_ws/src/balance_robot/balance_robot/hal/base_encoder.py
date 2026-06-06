from abc import ABC, abstractmethod
from typing import Optional

from balance_robot.msg import WheelState


class BaseEncoder(ABC):
    @abstractmethod
    def read(self) -> Optional[WheelState]:
        pass

    def close(self) -> None:
        pass
