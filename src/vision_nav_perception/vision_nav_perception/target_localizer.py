import rclpy
from rclpy.node import Node
import message_filters
from sensor_msgs.msg import Image, CameraInfo
from vision_msgs.msg import Detection2DArray
from geometry_msgs.msg import PointStamped, PoseStamped
from cv_bridge import CvBridge
import numpy as np
import tf2_ros
import tf2_geometry_msgs  # noqa: F401


class TargetLocalizer(Node):
    def __init__(self):
        super().__init__('target_localizer')
        self.bridge = CvBridge()
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.K = None
        self.create_subscription(CameraInfo, '/camera/camera_info', self.on_camera_info, 1)

        det_sub = message_filters.Subscriber(self, Detection2DArray, '/detections')
        depth_sub = message_filters.Subscriber(self, Image, '/camera/depth/image_raw')
        self.sync = message_filters.ApproximateTimeSynchronizer([det_sub, depth_sub], queue_size=10, slop=0.1)
        self.sync.registerCallback(self.on_synced_data)

        self.pose_pub = self.create_publisher(PoseStamped, '/target_pose', 10)
        self.get_logger().info('Target localizer started')

    def on_camera_info(self, msg):
        self.K = np.array(msg.k).reshape(3, 3)

    def on_synced_data(self, det_msg, depth_msg):
        if self.K is None or not det_msg.detections:
            return

        depth = self.bridge.imgmsg_to_cv2(depth_msg, desired_encoding='32FC1')
        best = max(det_msg.detections, key=lambda d: d.bbox.size_x * d.bbox.size_y)

        u = int(best.bbox.center.position.x)
        v = int(best.bbox.center.position.y)
        half_w = max(int(best.bbox.size_x * 0.15), 2)
        half_h = max(int(best.bbox.size_y * 0.15), 2)

        y0, y1 = max(v - half_h, 0), min(v + half_h, depth.shape[0])
        x0, x1 = max(u - half_w, 0), min(u + half_w, depth.shape[1])
        patch = depth[y0:y1, x0:x1]
        valid = patch[np.isfinite(patch) & (patch > 0.05) & (patch < 9.9)]

        if valid.size == 0:
            self.get_logger().warn(
                f'No valid depth. patch shape={patch.shape}, '
                f'min={np.nanmin(patch) if patch.size else "empty"}, '
                f'max={np.nanmax(patch) if patch.size else "empty"}, '
                f'nan_count={np.isnan(patch).sum()}, '
                f'inf_count={np.isinf(patch).sum()}, '
                f'u={u}, v={v}, depth_shape={depth.shape}')
            return

        Z = float(np.median(valid))
        fx, fy = self.K[0, 0], self.K[1, 1]
        cx, cy = self.K[0, 2], self.K[1, 2]
        X = (u - cx) * Z / fx
        Y = (v - cy) * Z / fy

        pt = PointStamped()
        pt.header = depth_msg.header
        pt.header.stamp = rclpy.time.Time().to_msg()
        pt.point.x = X
        pt.point.y = Y
        pt.point.z = Z

        try:
            pt_map = self.tf_buffer.transform(pt, 'map', timeout=rclpy.duration.Duration(seconds=0.3))
        except Exception as e:
            self.get_logger().warn(f'TF transform to map failed: {e}')
            return

        pose = PoseStamped()
        pose.header = pt_map.header
        pose.pose.position = pt_map.point
        pose.pose.orientation.w = 1.0
        self.pose_pub.publish(pose)
        self.get_logger().info(
            f'Target at map frame: x={pt_map.point.x:.2f}, y={pt_map.point.y:.2f}, z={pt_map.point.z:.2f}')


def main(args=None):
    rclpy.init(args=args)
    node = TargetLocalizer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
