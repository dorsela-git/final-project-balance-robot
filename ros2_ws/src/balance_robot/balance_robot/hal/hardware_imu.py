from typing import Optional

from sensor_msgs.msg import Imu

from balance_robot.hal.base_imu import BaseIMU


class HardwareIMU(BaseIMU):
    def __init__(self, logger):
        self._logger = logger
        self._logger.warn(
            'TODO: HardwareIMU selected, but BNO086 integration is not implemented yet.'
        )

    def read(self, stamp, frame_id: str) -> Optional[Imu]:
        return None
