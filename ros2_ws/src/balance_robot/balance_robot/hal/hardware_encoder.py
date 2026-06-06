from typing import Optional

from balance_robot.msg import WheelState

from balance_robot.hal.base_encoder import BaseEncoder


class HardwareEncoder(BaseEncoder):
    def __init__(self, logger):
        self._logger = logger
        self._logger.warn(
            'TODO: HardwareEncoder selected, but encoder GPIO integration is not implemented yet.'
        )

    def read(self) -> Optional[WheelState]:
        return None
