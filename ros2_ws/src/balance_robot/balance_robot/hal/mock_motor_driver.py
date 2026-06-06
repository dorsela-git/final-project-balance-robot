from balance_robot.hal.base_motor_driver import BaseMotorDriver


class MockMotorDriver(BaseMotorDriver):
    def __init__(self, logger):
        self._logger = logger

    def apply_command(self, left_motor: float, right_motor: float) -> None:
        self._logger.info(
            f'Received motor command: [{left_motor}, {right_motor}]'
        )

    def stop(self) -> None:
        self._logger.info('Motor stop requested.')

    def emergency_stop(self, reason: str) -> None:
        self._logger.warn(f'Emergency stop triggered: {reason}')
        self.stop()
