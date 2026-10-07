from setuptools import setup

package_name = 'vision_nav_perception'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='arun',
    maintainer_email='okerj849@gmail.com',
    description='Color-based and vision-based object detection',
    license='MIT',
    entry_points={
        'console_scripts': [
            'detector_node = vision_nav_perception.detector_node:main',
            'target_localizer = vision_nav_perception.target_localizer:main',
        ],
    },
)
