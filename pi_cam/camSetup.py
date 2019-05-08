from picamera import PiCamera
from time import sleep

def init():
    camera = PiCamera(sensor_mode=5, resolution=(112,80), framerate=30)
    print('resoultion: {}, {}'.format(
        camera.resolution.width,
        camera.resolution.height))
    print('sensor mode: {}'.format(
        camera.sensor_mode))
    print('framerate: {}'.format(
        camera.framerate))
    # return
    width = camera.resolution.width
    height = camera.resolution.height
    camera.brightness = 50
    sleep(2)
    print('Camera Adjusted')
    return camera