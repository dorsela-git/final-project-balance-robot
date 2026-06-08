from typing import Any, Optional

from balance_robot.hal.base_motor_driver import BaseMotorDriver


class HardwareMotorDriver(BaseMotorDriver):
    """DBH-12V H-bridge motor driver for Raspberry Pi GPIO via gpiozero."""

    def __init__(self, logger, node=None):
        self._logger = logger
        self._node = node
        self._gpio_ready = False
        self._readiness_logged = False

        self._left_in1 = None
        self._left_in2 = None
        self._left_en = None
        self._right_in1 = None
        self._right_in2 = None
        self._right_en = None

        self._left_in1_pin = None
        self._left_in2_pin = None
        self._left_en_pin = None
        self._right_in1_pin = None
        self._right_in2_pin = None
        self._right_en_pin = None
        self._pwm_frequency_hz = 1000.0
        self._max_command = 1.0

        self._load_parameters()
        self._initialize_gpio()
        self.stop()

    def _get_parameter(self, name: str, default: Any) -> Any:
        if self._node is None:
            return default
        if not self._node.has_parameter(name):
            self._node.declare_parameter(name, default)
        return self._node.get_parameter(name).value

    @staticmethod
    def _is_configured(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip().upper() != 'TODO' and value.strip() != ''
        return True

    @staticmethod
    def _parse_gpio_pin(value: Any) -> Optional[int]:
        if not HardwareMotorDriver._is_configured(value):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        pin_text = str(value).strip().upper()
        if pin_text.startswith('GPIO'):
            pin_text = pin_text[4:]
        return int(pin_text)

    def _parse_float_parameter(self, name: str, default: float) -> float:
        value = self._get_parameter(name, default)
        if not self._is_configured(value):
            return default
        return float(value)

    def _load_parameters(self) -> None:
        self._left_in1_pin = self._parse_gpio_pin(
            self._get_parameter('motors.left_in1_pin', 5),
        )
        self._left_in2_pin = self._parse_gpio_pin(
            self._get_parameter('motors.left_in2_pin', 6),
        )
        self._left_en_pin = self._parse_gpio_pin(
            self._get_parameter('motors.left_en_pin', 13),
        )
        self._right_in1_pin = self._parse_gpio_pin(
            self._get_parameter('motors.right_in1_pin', 'TODO'),
        )
        self._right_in2_pin = self._parse_gpio_pin(
            self._get_parameter('motors.right_in2_pin', 'TODO'),
        )
        self._right_en_pin = self._parse_gpio_pin(
            self._get_parameter('motors.right_en_pin', 'TODO'),
        )
        self._pwm_frequency_hz = self._parse_float_parameter(
            'motors.pwm_frequency_hz',
            1000.0,
        )
        self._max_command = self._parse_float_parameter('motors.max_command', 1.0)

    def _left_pins_configured(self) -> bool:
        return (
            self._left_in1_pin is not None
            and self._left_in2_pin is not None
            and self._left_en_pin is not None
        )

    def _right_pins_configured(self) -> bool:
        return (
            self._right_in1_pin is not None
            and self._right_in2_pin is not None
            and self._right_en_pin is not None
        )

    def _initialize_gpio(self) -> None:
        if not self._left_pins_configured():
            self._gpio_ready = False
            self._logger.warn(
                'HardwareMotorDriver is not ready: left motor GPIO pins are not configured'
            )
            return

        if self._max_command <= 0.0:
            self._gpio_ready = False
            self._logger.warn(
                'HardwareMotorDriver is not ready: motors.max_command must be positive'
            )
            return

        try:
            from gpiozero import OutputDevice, PWMOutputDevice
        except ImportError:
            self._gpio_ready = False
            self._logger.warn(
                'HardwareMotorDriver is not ready: gpiozero is unavailable in this environment'
            )
            return

        try:
            self._left_in1 = OutputDevice(self._left_in1_pin)
            self._left_in2 = OutputDevice(self._left_in2_pin)
            self._left_en = PWMOutputDevice(
                self._left_en_pin,
                frequency=self._pwm_frequency_hz,
            )
        except Exception as exc:
            self._gpio_ready = False
            self._logger.warn(
                'HardwareMotorDriver failed to initialize left motor on '
                f'GPIO{self._left_in1_pin}/GPIO{self._left_in2_pin}/GPIO{self._left_en_pin}: '
                f'{exc}'
            )
            return

        self._gpio_ready = True
        mode = 'left-only'
        if self._right_pins_configured():
            try:
                self._right_in1 = OutputDevice(self._right_in1_pin)
                self._right_in2 = OutputDevice(self._right_in2_pin)
                self._right_en = PWMOutputDevice(
                    self._right_en_pin,
                    frequency=self._pwm_frequency_hz,
                )
                mode = 'left and right'
            except Exception as exc:
                self._logger.warn(
                    'Right motor GPIO pins are configured but initialization failed; '
                    f'right motor commands will be ignored: {exc}'
                )
        else:
            self._logger.info(
                'Right motor pins are not configured; right motor commands will be ignored.'
            )

        self._logger.info(
            'HardwareMotorDriver ready in '
            f'{mode} mode: left IN1=GPIO{self._left_in1_pin}, '
            f'IN2=GPIO{self._left_in2_pin}, EN=GPIO{self._left_en_pin}, '
            f'pwm_frequency_hz={self._pwm_frequency_hz:.0f}, '
            f'max_command={self._max_command:.2f}'
        )

    @staticmethod
    def _clamp_command(command: float, max_command: float) -> float:
        return max(-max_command, min(max_command, command))

    def _log_readiness_once(self) -> None:
        if self._readiness_logged:
            return
        self._readiness_logged = True
        self._logger.warn(
            'HardwareMotorDriver commands are ignored because GPIO initialization '
            'did not succeed.'
        )

    def _stop_channel(
        self,
        in1: Optional[Any],
        in2: Optional[Any],
        enable: Optional[Any],
    ) -> None:
        if in1 is not None:
            in1.off()
        if in2 is not None:
            in2.off()
        if enable is not None:
            enable.off()

    def _apply_channel_command(
        self,
        command: float,
        in1: Optional[Any],
        in2: Optional[Any],
        enable: Optional[Any],
    ) -> None:
        clamped = self._clamp_command(command, self._max_command)
        if in1 is None or in2 is None or enable is None:
            return

        if clamped == 0.0:
            self._stop_channel(in1, in2, enable)
            return

        duty = abs(clamped) / self._max_command
        if clamped > 0.0:
            in1.on()
            in2.off()
        else:
            in1.off()
            in2.on()
        enable.value = duty

    def apply_command(self, left_motor: float, right_motor: float) -> None:
        if not self._gpio_ready:
            self._log_readiness_once()
            return

        self._apply_channel_command(
            left_motor,
            self._left_in1,
            self._left_in2,
            self._left_en,
        )
        if self._right_in1 is not None:
            self._apply_channel_command(
                right_motor,
                self._right_in1,
                self._right_in2,
                self._right_en,
            )

    def stop(self) -> None:
        if not self._gpio_ready:
            return

        self._stop_channel(self._left_in1, self._left_in2, self._left_en)
        self._stop_channel(self._right_in1, self._right_in2, self._right_en)

    def emergency_stop(self, reason: str) -> None:
        self._logger.warn(f'Emergency stop triggered: {reason}')
        self.stop()

    def close(self) -> None:
        self.stop()
        for device in (
            self._left_en,
            self._left_in1,
            self._left_in2,
            self._right_en,
            self._right_in1,
            self._right_in2,
        ):
            if device is not None:
                device.close()
        self._left_en = None
        self._left_in1 = None
        self._left_in2 = None
        self._right_en = None
        self._right_in1 = None
        self._right_in2 = None
