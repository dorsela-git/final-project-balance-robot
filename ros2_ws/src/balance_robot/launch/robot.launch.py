from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from pathlib import Path


def generate_launch_description():
    params_file = Path(
        get_package_share_directory('balance_robot'),
        'config',
        'robot_params.yaml',
    )

    return LaunchDescription([
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
    ])
