import json
import os
import time

from monodrive.simulator import Simulator


if __name__ == "__main__":
    root = os.path.dirname(__file__)

    trajectory = json.load(open(os.path.join(root, 'configurations', 'open_sense', 'SuddenStop.json')))
    simulator = Simulator(json.load(open(os.path.join(root, 'configurations', 'simulator.json'))),
                          json.load(open(os.path.join(root, 'configurations', 'sensors.json'))),
                          trajectory)

    #simulator.configure()
    # weather = json.load(open(os.path.join(root, 'configurations', 'weather.json')))
    # for profile in weather['profiles']:
    #     print(simulator.set_weather(profile['id']))
    #     time.sleep(5)

    # profile = weather['profiles'][10]
    # profile['id'] = 'test'
    # print(simulator.configure_weather({
    #     u'set_profile': u'test',
    #     u'profiles': [profile]
    # }))
    simulator.start()
    time.sleep(10)
    for i in range(0, len(trajectory)):
        simulator.step()
        time.sleep(.25)
