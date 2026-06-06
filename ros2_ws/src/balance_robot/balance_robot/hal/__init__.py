from balance_robot.hal.base_encoder import BaseEncoder
from balance_robot.hal.base_imu import BaseIMU
from balance_robot.hal.base_motor_driver import BaseMotorDriver
from balance_robot.hal.hardware_encoder import HardwareEncoder
from balance_robot.hal.hardware_imu import HardwareIMU
from balance_robot.hal.hardware_motor_driver import HardwareMotorDriver
from balance_robot.hal.mock_encoder import MockEncoder
from balance_robot.hal.mock_imu import MockIMU
from balance_robot.hal.mock_motor_driver import MockMotorDriver

__all__ = [
    'BaseEncoder',
    'BaseIMU',
    'BaseMotorDriver',
    'HardwareEncoder',
    'HardwareIMU',
    'HardwareMotorDriver',
    'MockEncoder',
    'MockIMU',
    'MockMotorDriver',
    'create_encoder',
    'create_imu',
    'create_motor_driver',
]


def create_imu(mode: str, logger) -> BaseIMU:
    if mode == 'hardware':
        return HardwareIMU(logger)
    return MockIMU()


def create_encoder(mode: str, logger, node=None) -> BaseEncoder:
    if mode == 'hardware':
        return HardwareEncoder(logger, node)
    return MockEncoder()


def create_motor_driver(mode: str, logger) -> BaseMotorDriver:
    if mode == 'hardware':
        return HardwareMotorDriver(logger)
    return MockMotorDriver(logger)
