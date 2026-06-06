from abc import ABC, abstractmethod


class BaseMotorDriver(ABC):
    @abstractmethod
    def apply_command(self, left_motor: float, right_motor: float) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def emergency_stop(self, reason: str) -> None:
        pass

    def close(self) -> None:
        self.stop()
