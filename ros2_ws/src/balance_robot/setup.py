from glob import glob

from setuptools import find_packages, setup

package_name = 'balance_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/msg', glob('msg/*.msg')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Dor Sela',
    maintainer_email='dor.sela@example.com',
    description='ROS 2 package for balance_robot.',
    license='MIT',
    tests_require=['pytest'],
    options={
        'install': {
            'install_scripts': '$base/lib/' + package_name,
        },
    },
    entry_points={
        'console_scripts': [
            'imu_node = balance_robot.imu_node:main',
            'encoder_node = balance_robot.encoder_node:main',
            'state_estimator_node = balance_robot.state_estimator_node:main',
            'lqr_controller_node = balance_robot.lqr_controller_node:main',
            'motor_node = balance_robot.motor_node:main',
            'diagnostics_node = balance_robot.diagnostics_node:main',
            'safety_state_node = balance_robot.safety_state:main',
        ],
    },
)
