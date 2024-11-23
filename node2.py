#!/usr/bin/env python3

import rospy
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32
import math

# Global variables for positions
turtle1_pose = None
turtle2_pose = None

# Thresholds
DISTANCE_THRESHOLD = 1.0
BOUNDARY_LIMIT = 1.0
MAX_BOUNDARY = 10.0

# Callback for turtle1 pose updates
def turtle1_pose_callback(msg):
    global turtle1_pose
    turtle1_pose = msg

# Callback for turtle2 pose updates
def turtle2_pose_callback(msg):
    global turtle2_pose
    turtle2_pose = msg

# Calculate the distance between turtle1 and turtle2
def calculate_distance():
    if turtle1_pose and turtle2_pose:
        x1, y1 = turtle1_pose.x, turtle1_pose.y
        x2, y2 = turtle2_pose.x, turtle2_pose.y
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return None

# Stop the turtle
def stop_turtle(turtle_name):
    pub = rospy.Publisher(f'/{turtle_name}/cmd_vel', Twist, queue_size=10)
    stop_msg = Twist()
    pub.publish(stop_msg)
    rospy.loginfo(f"{turtle_name} has been stopped.")

# Wait for turtle2 to be available
def wait_for_turtle2():
    rospy.loginfo("Waiting for turtle2 to be spawned...")
    while not rospy.is_shutdown():
        topics = rospy.get_published_topics()
        if any('/turtle2/pose' in topic for topic, _ in topics):
            rospy.loginfo("turtle2 is available.")
            return
        rospy.sleep(1)

# Main function
def main():
    rospy.init_node('node2', anonymous=True)
    rospy.loginfo("Node 2 (Distance Checker) Started")

    wait_for_turtle2()

    rospy.Subscriber('/turtle1/pose', Pose, turtle1_pose_callback)
    rospy.Subscriber('/turtle2/pose', Pose, turtle2_pose_callback)
    distance_pub = rospy.Publisher('/turtle_distance', Float32, queue_size=10)

    rate = rospy.Rate(10)  # 10 Hz

    while not rospy.is_shutdown():
        if turtle1_pose and turtle2_pose:
            distance = calculate_distance()
            if distance is not None:
                distance_pub.publish(distance)
                rospy.loginfo(f"Distance: {distance}")

                if distance < DISTANCE_THRESHOLD:
                    rospy.logwarn("Turtles too close! Stopping.")
                    stop_turtle('turtle1')
                    stop_turtle('turtle2')

            # Check boundaries for turtle1
            if (turtle1_pose.x < BOUNDARY_LIMIT or turtle1_pose.x > MAX_BOUNDARY or
                turtle1_pose.y < BOUNDARY_LIMIT or turtle1_pose.y > MAX_BOUNDARY):
                rospy.logwarn("Turtle1 near boundary! Stopping.")
                stop_turtle('turtle1')

            # Check boundaries for turtle2
            if (turtle2_pose.x < BOUNDARY_LIMIT or turtle2_pose.x > MAX_BOUNDARY or
                turtle2_pose.y < BOUNDARY_LIMIT or turtle2_pose.y > MAX_BOUNDARY):
                rospy.logwarn("Turtle2 near boundary! Stopping.")
                stop_turtle('turtle2')

        rate.sleep()

if __name__ == "__main__":
    main()


