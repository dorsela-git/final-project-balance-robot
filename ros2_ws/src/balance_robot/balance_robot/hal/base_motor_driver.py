from abc import ABC, abstractmethod


class BaseMotorDriver(ABC):
    @abstractmethod
    def apply_command(self, left_motor: float, right_motor: float) -> None:
        pass

    def stop(self) -> None:
        self.apply_command(0.0, 0.0)

    def close(self) -> None:
        self.stop()
