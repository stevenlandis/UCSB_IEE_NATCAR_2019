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
        lastSpeed = 120
        motorControl.speed(lastSpeed)

        lastX = 25

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
            'did turn',
            'set speed'])
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
            timer.tick() # get image array

            # convert array into rgb PIL image
            img = Image.fromarray(imgArr, 'RGB')
            timer.tick() # got image from array

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
                servoControl.turn(0)
                sleep(0.2)
                # img.save('end.png')
                return
            timer.tick() # tested for end

            # resize image for faster path finding
            img = img.resize((50, 50), Image.ANTIALIAS)
            greyImg = picUtils.imgFilter(img, threshold)
            data = picUtils.getImgArray(greyImg)
            timer.tick() # filtered image

            # do pathfinding
            p0 = picUtils.getFirstPos(data, lastX)
            if p0 != None:
                lastX = int(p0[0] + int(10*lastTurn))
                lastX = max(0, min(49, lastX))
                # print(p0[0],lastTurn,lastX)
                points = picUtils.fillSearch(data, p0, lastTurn)
                timer.tick() # got line points
                points = pnt.transformPoints(points)
                timer.tick() # transformed points
                points = pnt.filterPoints(points, 4)
                timer.tick() # filterd points
                a = picUtils.getTurn(points, 100000)
                lastTurn = a

            # turn to most recent turn
            servoControl.turn(lastTurn)
            timer.tick()

            # set the speed to the turn
            # motorControl.speed(servoControl.getSpeed(lastTurn));
            timer.tick()

            # print(timer)

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