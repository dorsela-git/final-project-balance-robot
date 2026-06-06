from balance_robot.hal.base_motor_driver import BaseMotorDriver


class HardwareMotorDriver(BaseMotorDriver):
    def __init__(self, logger):
        self._logger = logger
        self._logger.warn(
            'TODO: HardwareMotorDriver selected, but motor driver integration is not implemented yet.'
        )

    def apply_command(self, left_motor: float, right_motor: float) -> None:
        self._logger.warn(
            'TODO: apply_command() is not implemented for hardware motor driver.'
        )

    def stop(self) -> None:
        self._logger.warn(
            'TODO: stop() is not implemented for hardware motor driver.'
        )

    def emergency_stop(self, reason: str) -> None:
        self._logger.warn(
            f'TODO: emergency_stop() is not implemented for hardware motor driver. Reason: {reason}'
        )
