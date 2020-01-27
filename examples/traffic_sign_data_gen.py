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
import matplotlib.pyplot as plt
import cv2
from datetime import datetime

# src
from monodrive.simulator import Simulator
from monodrive.sensors import *

# constants
VERBOSE = False
DISPLAY = False
RECORD = True

# global
lock = threading.RLock()
processing = 0
running = True
camera_frame = None

weathers = ["Clear1", "Clear2", "Rain1", "Rain2", "Twilight1", "Twilight2"]
sensors = ["tcd_1.json", "tcd_2.json", "tcd_3.json"]
data_storage_path = "D:/tcd_data"
MIN_BOX_SIZE = 32*32

class_map = {}

def camera_on_update(frame: CameraFrame):
    """
    callback to process parsed camera data
    """
    if VERBOSE:
        print("Perception system with image size {0}".format(frame.image.shape))
        if frame.annotation:
            print("Annotation info: \n{0}".format(frame.annotation))
    global camera_frame

    camera_frame = frame
    with lock:
        global processing
        processing -= 1


def state_on_update(frame: StateFrame):
    """
    callback to process parsed state sensor data
    """
    if VERBOSE:
        print("State sensor reporting {0} objects".format(len(frame.object_list)))
    with lock:
        global processing
        processing -= 1


def get_actor_classification(annotation):
    actor_class = ""
    tags = annotation["tags"]
    isTrafficSign = False
    for tag in tags:
        if "traffic" in tag and "sign" in tag:
            isTrafficSign = True
    if not isTrafficSign:
        return actor_class

    tags.sort()
    for tag in tags:
        if "TCD" in tag or "traffic" in tag:
            continue
        tag = tag.replace(':', '-')
        actor_class += tag + "_"
    if len(actor_class) > 0:
        actor_class = actor_class[:-1]
    # print(actor_class)
    return actor_class


def save_images(dir_name, frame):
    if not camera_frame:
        return
    global class_map

    # img = np.array(frame.image[..., ::-1])
    img = np.array(frame.image)
    for actor_annotation in camera_frame.annotation:
        actor_class = get_actor_classification(actor_annotation)
        if actor_class == "":
            continue

        for primitive_annotation in actor_annotation["2d_bounding_boxes"]:
            if primitive_annotation["name"] == "face":
                bound_box = [int(x) for x in primitive_annotation["2d_bounding_box"]]
                size = (bound_box[1] - bound_box[0], bound_box[3] - bound_box[2])
                if size[0] * size[1] < MIN_BOX_SIZE or bound_box[1] < bound_box[0] or bound_box[3] < bound_box[2]:
                    continue

                # print(img.shape, bound_box)
                sign_face = img[bound_box[2]:bound_box[3], bound_box[0]:bound_box[1], ...]
                if actor_class in class_map:
                    class_map[actor_class] += 1
                else:
                    class_map[actor_class] = 0
                id_number = class_map[actor_class]
                class_dir = os.path.join(dir_name, actor_class)
                if not os.path.exists(class_dir):
                    os.makedirs(class_dir)
                file_path = os.path.join(class_dir, str(id_number) + ".png")
                # print(file_path)
                cv2.imwrite(file_path, sign_face)


def run_case(root, weather, sensor):
    # Construct simulator from file
    simulator = Simulator.from_file(
        os.path.join(root, 'configurations', 'annotated_camera_simulator.json'),
        trajectory=os.path.join(root, 'trajectories', 'tcd_replay_60mph_full.json'),
        sensors=os.path.join(root, 'configurations', sensor),
        ego=os.path.join(root, 'configurations', 'vehicle.json'),
        verbose=VERBOSE
    )

    # weather_file = open(os.path.join(root, 'configurations', 'traffic_sign_weather.json'), 'r'),
    weather_file = open(os.path.join(root, 'configurations', 'traffic_sign_weather.json'))
    print(os.path.join(root, 'configurations', 'traffic_sign_weather.json'))
    weather_json = json.load(weather_file)
    weather_json["set_profile"] = weather
    print(json.dumps(weather_json))


    dir_name = weather + "_" + os.path.splitext(sensor)[0] + "_" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    instance_storage_path = os.path.join(data_storage_path, dir_name)

    # Start the simulation
    simulator.start()
    print('Starting simulator')
    try:
        # Subscribe to sensors of interest
        simulator.subscribe_to_sensor('Camera_8000', camera_on_update)
        simulator.configure_weather(weather_json)

        # Start stepping the simulator
        time_steps = []

        # setup display
        if DISPLAY:
            fig = plt.figure('image annotations', figsize=(12, 12))
            ax_camera = fig.gca()
            ax_camera.set_axis_off()

            fig.canvas.draw()
            data_camera = None

        for i in range(simulator.num_steps):
            start_time = time.time()

            # expect 2 sensors to be processed
            with lock:
                global processing
                processing = 1

            # send step command
            response = simulator.step()
            print(response)

            # wait for processing to complete
            while running:
                with lock:
                    if processing == 0:
                        break
                time.sleep(0.05)

            # plot if needed
            global camera_frame
            if RECORD:
                save_images(instance_storage_path, camera_frame)
            if DISPLAY:
                # update with camera data
                if camera_frame:
                    img = np.array(camera_frame.image[..., ::-1])
                    for actor_annotation in camera_frame.annotation:
                        for primitive_annotation in actor_annotation["2d_bounding_boxes"]:
                            box = primitive_annotation["2d_bounding_box"]
                            top_left = (int(box[0]), int(box[2]))
                            bottom_right = (int(box[1]), int(box[3]))
                            cv2.rectangle(img, top_left, bottom_right, (255, 0, 0), 1)

                    if data_camera is None:
                        data_camera = ax_camera.imshow(img)
                    else:
                        data_camera.set_data(img)

                # do draw
                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.0001)

            # timing
            dt = time.time() - start_time
            time_steps.append(dt)
            if VERBOSE:
                print("Step = {0} completed in {1:.2f}ms".format(i, (dt * 1000), 2))
                print("------------------")
            # time.sleep(1)
            if running is False:
                break

        fps = 1.0 / (sum(time_steps) / len(time_steps))
        print('Average FPS: {}'.format(fps))

    except Exception as e:
        print(e)

    print("Stopping the simulator.")
    simulator.stop()


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

    for weather in weathers:
        for sensor in sensors:
            run_case(root, weather, sensor)




if __name__ == "__main__":
    main()
