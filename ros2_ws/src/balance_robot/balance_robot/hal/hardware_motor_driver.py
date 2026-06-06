from balance_robot.hal.base_motor_driver import BaseMotorDriver


class HardwareMotorDriver(BaseMotorDriver):
    def __init__(self, logger):
        self._logger = logger
        self._logger.warn(
            'TODO: HardwareMotorDriver selected, but motor driver integration is not implemented yet.'
        )

    def apply_command(self, left_motor: float, right_motor: float) -> None:
        pass
