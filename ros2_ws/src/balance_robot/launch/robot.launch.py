import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import OpaqueFunction
from launch_ros.actions import Node
from pathlib import Path


def _load_teleop_enabled(params_file: Path) -> bool:
    with params_file.open('r', encoding='utf-8') as params_stream:
        params = yaml.safe_load(params_stream)
    return bool(params['/**']['ros__parameters']['teleop']['enabled'])


def _launch_setup(context, *args, **kwargs):
    params_file = Path(
        get_package_share_directory('balance_robot'),
        'config',
        'robot_params.yaml',
    )
    teleop_enabled = _load_teleop_enabled(params_file)

    nodes = [
        Node(
            package='balance_robot',
            executable='imu_node',
            name='imu_node',
            output='screen',
            parameters=[str(params_file)],
        ),
        Node(
            package='balance_robot',
            executable='encoder_node',
            name='encoder_node',
            output='screen',
            parameters=[str(params_file)],
        ),
        Node(
            package='balance_robot',
            executable='state_estimator_node',
            name='state_estimator_node',
            output='screen',
            parameters=[str(params_file)],
        ),
        Node(
            package='balance_robot',
            executable='lqr_controller_node',
            name='lqr_controller_node',
            output='screen',
            parameters=[str(params_file)],
        ),
        Node(
            package='balance_robot',
            executable='safety_state_node',
            name='safety_state_node',
            output='screen',
            parameters=[str(params_file)],
        ),
        Node(
            package='balance_robot',
            executable='motor_node',
            name='motor_node',
            output='screen',
            parameters=[str(params_file)],
        ),
        Node(
            package='balance_robot',
            executable='diagnostics_node',
            name='diagnostics_node',
            output='screen',
            parameters=[str(params_file)],
        ),
    ]

    if teleop_enabled:
        nodes.append(
            Node(
                package='balance_robot',
                executable='teleop_node',
                name='teleop_node',
                output='screen',
                parameters=[str(params_file)],
            )
        )

    return nodes


def generate_launch_description():
    return LaunchDescription([
        OpaqueFunction(function=_launch_setup),
    ])
