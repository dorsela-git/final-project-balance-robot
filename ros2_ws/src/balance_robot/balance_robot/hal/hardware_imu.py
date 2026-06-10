from typing import Any, Optional

from sensor_msgs.msg import Imu

from balance_robot.hal.base_imu import BaseIMU


class HardwareIMU(BaseIMU):
    """Adafruit BNO086 I2C IMU foundation for Raspberry Pi integration."""

    def __init__(self, logger, node=None):
        self._logger = logger
        self._node = node
        self._device_ready = False
        self._readiness_logged = False
        self._initialized = False

        self._imu_type = 'bno086'
        self._interface = 'i2c'
        self._i2c_bus = 1
        self._i2c_address = 0x4A
        self._frame_id = 'imu_link'
        self._publish_rate_hz = 50.0

        self._load_parameters()
        self._initialize_device()

    def _get_parameter(self, name: str, default: Any) -> Any:
        if self._node is None:
            return default
        if not self._node.has_parameter(name):
            return default
        return self._node.get_parameter(name).value

    @staticmethod
    def _is_configured(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip().upper() != 'TODO' and value.strip() != ''
        return True

    def _parse_int_parameter(self, name: str, default: int = 0) -> int:
        value = self._get_parameter(name, default)
        if not self._is_configured(value):
            return default
        if isinstance(value, str):
            return int(value, 0)
        return int(value)

    def _parse_float_parameter(self, name: str, default: float = 0.0) -> float:
        value = self._get_parameter(name, default)
        if not self._is_configured(value):
            return default
        return float(value)

    def _load_parameters(self) -> None:
        self._imu_type = self._get_parameter('imu.type', 'bno086')
        self._interface = self._get_parameter('imu.interface', 'i2c')
        self._i2c_bus = self._parse_int_parameter('imu.i2c_bus', 1)
        self._i2c_address = self._parse_int_parameter('imu.i2c_address', 0x4A)
        self._frame_id = self._get_parameter('imu.frame_id', 'imu_link')
        self._publish_rate_hz = self._parse_float_parameter(
            'imu.publish_rate_hz',
            50.0,
        )

    def _detect_bno08x_library(self) -> Optional[str]:
        try:
            import adafruit_bno08x  # noqa: F401
            return 'adafruit_bno08x'
        except ImportError:
            pass

        try:
            import board  # noqa: F401
            import busio  # noqa: F401
            return 'circuitpython_busio'
        except ImportError:
            return None

    def _initialize_device(self) -> None:
        interface_ready = self._interface.lower() == 'i2c'
        type_ready = self._imu_type.lower() in {'bno086', 'bno085', 'bno08x'}
        bus_ready = self._i2c_bus > 0
        address_ready = self._i2c_address > 0
        library_name = self._detect_bno08x_library()

        if (
            interface_ready
            and type_ready
            and bus_ready
            and address_ready
            and library_name is not None
        ):
            self._device_ready = False
            self._logger.warn(
                'TODO: Adafruit BNO086 parameters and library are available, '
                'but I2C device initialization is not implemented yet.'
            )
            return

        reasons = []
        if not interface_ready:
            reasons.append(f'interface "{self._interface}" is not supported yet')
        if not type_ready:
            reasons.append(f'imu type "{self._imu_type}" is not supported yet')
        if not bus_ready:
            reasons.append('I2C bus is not configured')
        if not address_ready:
            reasons.append('I2C address is not configured')
        if library_name is None:
            reasons.append('Adafruit BNO08x library is unavailable in this environment')

        self._device_ready = False
        self._logger.warn(
            'TODO: HardwareIMU is not ready for Adafruit BNO086: '
            + '; '.join(reasons)
        )

    def _zero_imu(self, stamp, frame_id: str) -> Imu:
        msg = Imu()
        msg.header.stamp = stamp
        msg.header.frame_id = frame_id or self._frame_id
        msg.orientation.w = 1.0
        return msg

    def _log_readiness_once(self) -> None:
        if self._readiness_logged:
            return
        self._readiness_logged = True
        self._logger.warn(
            'TODO: HardwareIMU read() is returning safe zero IMU data until '
            'Adafruit BNO086 I2C integration is implemented.'
        )

    def reset(self) -> None:
        self._initialized = False

    def read(self, stamp, frame_id: str) -> Optional[Imu]:
        if not self._device_ready:
            self._log_readiness_once()
            return self._zero_imu(stamp, frame_id)

        self._initialized = True
        return self._zero_imu(stamp, frame_id)

    def close(self) -> None:
        self.reset()
