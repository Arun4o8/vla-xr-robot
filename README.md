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
