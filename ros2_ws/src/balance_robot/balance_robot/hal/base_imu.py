from abc import ABC, abstractmethod
from typing import Optional

from sensor_msgs.msg import Imu


class BaseIMU(ABC):
    @abstractmethod
    def read(self, stamp, frame_id: str) -> Optional[Imu]:
        pass

    def close(self) -> None:
        pass
