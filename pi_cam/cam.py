from picamera import PiCamera
from time import sleep, time
import io
from PIL import Image, ImageOps
import numpy as np
import picUtils
import points as pnt
import servoControl
import motorControl
import camSetup
from threshold import threshold
from Timer import Timer

def main():
    camera = camSetup.init()
    width = camera.resolution.width
    height = camera.resolution.height

    servoControl.init()

    # declare inside main so outputs() has access
    # to width and height
    def outputs():
        lastSpeed = 40
        motorControl.speed(lastSpeed)

        stream = io.BytesIO()
        i = 0
        lastTurn = 0
        timer = Timer([
            'got image array',
            'got image from array',
            'tested for end',
            'filtered image',
            'got line points',
            'transformed points',
            'filtered points',
            'got approximate turn',
            'did turn'])
        maxY = pnt.transform((25,0))[1] - 10
        print('max Y: {}'.format(maxY))
        while True:
        # for i in range(40):
            yield stream
            # print('took picture {}'.format(i))
            timer.reset()

            # format pixels as array
            imgArr = []
            stream.seek(0)
            with stream.getbuffer() as view:
                imgArr = np.array(view)
                imgArr = imgArr.reshape(height, width, 3)
            timer.tick()

            # convert array into rgb PIL image
            img = Image.fromarray(imgArr, 'RGB')
            timer.tick()

            # # set threshold
            # if True or threshold == None:
            #     d = np.array(ImageOps.grayscale(img).getdata())
            #     d = (d - d.mean()) / d.std()
            #     threshold = 
            #     print('threshold: {}'.format(threshold))

            # get grayscale array for stopping
            greyImg = picUtils.imgFilter(img, threshold)
            stopData = picUtils.getImgArray(greyImg)
            if picUtils.isEnd(stopData):
                print('Is End {}'.format(i))
                return
            timer.tick()

            # resize image for faster path finding
            img = img.resize((50, 50), Image.ANTIALIAS)
            greyImg = picUtils.imgFilter(img, threshold)
            data = picUtils.getImgArray(greyImg)
            timer.tick()

            # do pathfinding
            points = picUtils.fillSearch(data, picUtils.getFirstPos(data, lastTurn))
            timer.tick()
            if points != None:
                points = pnt.transformPoints(points)
                timer.tick()
                points = pnt.filterPoints(points, 4)
                timer.tick()
                a = picUtils.getTurn(points, maxY)
                # convert a
                a = 0.444326*a-0.127358
                lastTurn = min(1, max(-1, a))

            # turn to most recent turn
            servoControl.turn(lastTurn)
            timer.tick()

            print(timer)

            # reset the stream
            stream.seek(0)
            stream.truncate()

    print('starting captures')
    try:
        camera.capture_sequence(outputs(), 'rgb', use_video_port=True)
    finally:
        print('Closing Camera')
        camera.close()
        motorControl.speed(0)

main()