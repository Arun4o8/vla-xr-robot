import math
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose


class MissionManager(Node):
    def __init__(self):
        super().__init__('mission_manager')

        self.declare_parameter('standoff_distance', 0.6)
        self.declare_parameter('resend_threshold', 0.3)
        self.standoff_distance = self.get_parameter('standoff_distance').value
        self.resend_threshold = self.get_parameter('resend_threshold').value

        self.last_goal_xy = None
        self.goal_in_progress = False

        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.create_subscription(
            PoseStamped, '/target_pose', self.on_target_pose, 10)

        self.get_logger().info('Mission manager started, waiting for Nav2 action server...')
        self.nav_client.wait_for_server()
        self.get_logger().info('Nav2 action server available. Ready.')

    def on_target_pose(self, msg: PoseStamped):
        target_x = msg.pose.position.x
        target_y = msg.pose.position.y

        if self.last_goal_xy is not None:
            dx = target_x - self.last_goal_xy[0]
            dy = target_y - self.last_goal_xy[1]
            if math.hypot(dx, dy) < self.resend_threshold:
                return  # target hasn't moved meaningfully, don't spam Nav2

        if self.goal_in_progress:
            return  # wait for current goal to finish before sending a new one

        # Compute a standoff point: back off from the target toward the origin
        # (a simple placeholder; a smarter version would back off toward the
        # robot's current position using TF, planned for a later iteration)
        dist = math.hypot(target_x, target_y)
        if dist < 1e-3:
            goal_x, goal_y = target_x, target_y
        else:
            scale = max(dist - self.standoff_distance, 0.0) / dist
            goal_x = target_x * scale
            goal_y = target_y * scale

        goal_msg = NavigateToPose.Goal()
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        goal_pose.pose.position.x = goal_x
        goal_pose.pose.position.y = goal_y

        # Face the goal toward the original target
        yaw = math.atan2(target_y - goal_y, target_x - goal_x)
        goal_pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal_pose.pose.orientation.w = math.cos(yaw / 2.0)

        goal_msg.pose = goal_pose

        self.get_logger().info(
            f'Sending Nav2 goal: x={goal_x:.2f}, y={goal_y:.2f} '
            f'(target was x={target_x:.2f}, y={target_y:.2f})')

        self.goal_in_progress = True
        self.last_goal_xy = (target_x, target_y)

        send_future = self.nav_client.send_goal_async(goal_msg)
        send_future.add_done_callback(self.on_goal_response)

    def on_goal_response(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Nav2 rejected the goal')
            self.goal_in_progress = False
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.on_goal_result)

    def on_goal_result(self, future):
        self.get_logger().info('Nav2 goal finished (reached, aborted, or canceled)')
        self.goal_in_progress = False


def main(args=None):
    rclpy.init(args=args)
    node = MissionManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
