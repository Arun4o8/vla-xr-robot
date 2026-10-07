# Vision-Language-Action Robot with Spatial Memory and XR Visualization

## Stage 0 — Environment Setup Complete

Stack: WSL2 + Ubuntu 22.04 + ROS 2 Humble + Gazebo 11 + Nav2 + TurtleBot3 Waffle

Working: robot spawns in Gazebo, AMCL localizes against a static map, Nav2 plans and drives to goals while avoiding obstacles.

### WSL2-specific fixes applied
- Gazebo model database hang: export GAZEBO_MODEL_DATABASE_URI=""
- Missing built-in models: export GAZEBO_MODEL_PATH=/usr/share/gazebo-11/models:/opt/ros/humble/share/turtlebot3_gazebo/models
- Gazebo transport corruption from /etc/hosts 127.0.1.1 mismatch: export GAZEBO_IP=127.0.0.1 and GAZEBO_MASTER_URI=http://127.0.0.1:11345
- RViz2 software-rendering fallback: fixed with `wsl --update` + `wsl --shutdown` from PowerShell

## Roadmap
- [x] Stage 0 - Environment setup
- [ ] Stage 1 - Grounded navigation (YOLO-World + depth + Nav2)
- [ ] Stage 2 - Language understanding
- [ ] Stage 3 - Spatial memory
- [ ] Stage 4 - XR visualization

### Known challenges solved

1. Sim-to-real domain gap with YOLO-World: open-vocabulary detectors are trained on photographic imagery and failed to recognize Gazebo's flat-shaded, untextured 3D models. Verified this wasn't a bug by testing the same model and prompts on a real photo, which worked fine. Solution for the simulation stage: classical HSV color-thresholding plus contour detection as a placeholder, with YOLO-World planned once the Gazebo world has photographic textures.

2. TurtleBot3 Waffle has no depth camera in Gazebo by default: edited the robot's SDF model to change the camera sensor from type="camera" to type="depth", which the existing libgazebo_ros_camera.so plugin supports natively in ROS 2. Also reduced camera resolution from 1920x1080 to 640x480 for WSL2 performance.

3. ROS 2 Python packages need setup.cfg: ament_python packages install console-script executables to bin/ by default, but ros2 run only looks in install/pkg/lib/pkg/. Fixed by adding a setup.cfg with script-dir and install-scripts pointing to lib/package_name.

4. TF "extrapolation into the future" errors: depth and detection message timestamps occasionally arrived slightly ahead of tf2's buffer. Fixed by requesting the transform at the latest available time instead of the exact message timestamp.

5. RViz2 becomes unresponsive under heavy multi-node load: with Gazebo, Nav2, RViz2, and three custom Python nodes plus PyTorch all running simultaneously in WSL2, RViz2's message queues overflow and the UI lags significantly, though it does eventually catch up. Confirmed this doesn't block the actual pipeline; Nav2 and the custom nodes keep running correctly underneath.

6. WSL2-specific Gazebo networking and rendering fixes: see Stage 0 section below.

---

## Stage 0 — Environment Setup

Stack: WSL2 + Ubuntu 22.04 + ROS 2 Humble + Gazebo 11 + Nav2 + TurtleBot3 Waffle

### Known WSL2 issues and fixes

1. Gazebo factory plugin never loads: caused by GAZEBO_MODEL_DATABASE_URI hanging and missing GAZEBO_MODEL_PATH. Fixed with export GAZEBO_MODEL_DATABASE_URI="" and export GAZEBO_MODEL_PATH=/usr/share/gazebo-11/models:/opt/ros/humble/share/turtlebot3_gazebo/models

2. Gazebo transport corruption: caused by /etc/hosts mapping the hostname to 127.0.1.1 instead of 127.0.0.1. Fixed with export GAZEBO_IP=127.0.0.1 and export GAZEBO_MASTER_URI=http://127.0.0.1:11345

3. RViz2 software-rendering fallback: fixed from Windows PowerShell with wsl --update then wsl --shutdown

### Permanent environment variables in ~/.bashrc
export GAZEBO_IP=127.0.0.1
export GAZEBO_MASTER_URI=http://127.0.0.1:11345
export GAZEBO_MODEL_PATH=/usr/share/gazebo-11/models:/opt/ros/humble/share/turtlebot3_gazebo/models
export TURTLEBOT3_MODEL=waffle

---

## Roadmap
- [x] Stage 0 - Environment setup
- [x] Stage 1 - Grounded navigation (color-based detection + depth + Nav2)
- [ ] Stage 2 - Language understanding
- [ ] Stage 3 - Spatial memory
- [ ] Stage 4 - XR visualization
