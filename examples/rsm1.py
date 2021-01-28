"""example.py
An example of creating a simulator and processing the sensor outputs.
"""
# lib
import json
import os
import time
import signal
import threading
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import open3d as o3d
import matplotlib.cm as cm

# src
from monodrive.simulator import Simulator
from monodrive.sensors import *

# constants
VERBOSE = True
DISPLAY = True

# global
# lock = threading.RLock()
lock = threading.Lock()
processing = 0
running = True
lidar_frame = None
vis = o3d.visualization.Visualizer()
rendered_pc = o3d.geometry.PointCloud()
colors = None
points = None
cmap = None


def lidar_on_update(frame: M1Frame):
    """
    callback to process parsed lidar data
    """
    if VERBOSE:
        print("LiDAR point cloud with size {0}".format(len(frame.points)))
    global points, colors, cmap
    pts = [[x.x/100, -x.y/100, x.z/100] for x in frame.points]
    # cs = [cmap((c.laser_id + 1) / 5)[:3] for c in frame.points]
    cs = [cmap((c.intensity*5) / 255)[:3] for c in frame.points]
    # cs = [[c.intensity / 255, 0 ,0] for c in frame.points]
    # cs = [cmap(c.laser_id)[:3] for c in frame.points]
    colors = o3d.utility.Vector3dVector(cs)
    points = o3d.utility.Vector3dVector(pts)
    # with lock:
    print("lidar processed")
    global processing
    processing -= 1


def perception_and_control():
    # TODO, process sensor data and determine control values to send to ego
    # return 1, 0, 0, 1  # fwd, right, brake, mode
    return 0.0, 0, 0, 1  # fwd, right, brake, mode


def main():
    """
    main driver function
    """
    root = os.path.dirname(__file__)

    # Flag to allow user to stop the simulation from SIGINT
    global running

    def handler(signum, frame):
        """"Signal handler to turn off the simulator with ctl+c"""
        global running
        running = False

    signal.signal(signal.SIGINT, handler)

    # Construct simulator from file
    simulator = Simulator.from_file(
        os.path.join(root, 'configurations', 'simulator_closed_loop.json'),
        scenario=os.path.join(root, 'scenarios', 'closed_loop.json'),
        sensors=os.path.join(root, 'configurations', 'sensors_rsm1.json'),
        weather=os.path.join(root, 'configurations', 'weather.json'),
        verbose=VERBOSE
    )

    # Start the simulation
    simulator.start()
    print('Starting simulator')
    try:
        # Subscribe to sensors of interest
        simulator.subscribe_to_sensor('RSM1Lidar_8200', lidar_on_update)

        # Start stepping the simulator
        time_steps = []

        # setup display
        if DISPLAY:
            global vis, rendered_pc, cmap
            cmap = cm.get_cmap("jet")
            # vis = o3d.visualization.Visualizer()
            # vis.create_window()
            # origin_mesh = o3d.geometry.TriangleMesh.create_coordinate_frame()
            # origin_mesh.scale(0.5, (0, 0, 0))
            # vis.add_geometry(origin_mesh)
            # vis.add_geometry(rendered_pc)
            # ctr = vis.get_view_control()
            # ctr.rotate(np.pi/2, np.pi/2)

        while running:
            start_time = time.time()
            global processing
            # expect x sensors to be processed
            with lock:
                processing = 1

            # compute and send vehicle control command
            forward, right, brake, drive_mode = perception_and_control()
            if VERBOSE:
                print("sending control: {0}, {1}, {2}, {3}".format(
                    forward, right, brake, drive_mode
                ))

            response = simulator.send_control(forward, right, brake, drive_mode)
            if VERBOSE:
                print(response)

            response = simulator.sample_sensors()
            if VERBOSE:
                print(response)

            # wait for processing to complete
            while running:
                # success = lock.acquire(False)
                with lock:
                # if success:
                    if processing == 0:
                        # lock.release()
                        break
                    # else:
                    #     lock.release()
                time.sleep(0.05)

            print("Updating Point Cloud")
            # plot if needed
            if DISPLAY:
                global points, colors
                # update with lidar data
                if points:
                    rendered_pc.points = points
                    rendered_pc.colors = colors
                    print("Finished Updating Point Cloud")
                    print("Updating render")
                    # vis.update_geometry(rendered_pc)
                    # vis.update_renderer()
                    origin_mesh = o3d.geometry.TriangleMesh.create_coordinate_frame()
                    # origin_mesh.scale(100, (0, 0, 0))
                    o3d.visualization.draw_geometries([rendered_pc, origin_mesh])
                    print("Finished updating render")

            # timing
            dt = time.time() - start_time
            time_steps.append(dt)
            if VERBOSE:
                print("Step = {0} completed in {1:.2f}ms".format(len(time_steps), (dt * 1000), 2))
                print("------------------")
            if running is False:
                break

        fps = 1.0 / (sum(time_steps) / len(time_steps))
        print('Average FPS: {}'.format(fps))
    except Exception as e:
        print(e)

    print("Stopping the simulator.")
    simulator.stop()


if __name__ == "__main__":
    main()
