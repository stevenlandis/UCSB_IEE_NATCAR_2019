from picamera import PiCamera
from time import sleep, time
import io
from PIL import Image
import numpy as np
# from picUtils import imgFilter, getImgArray, fillSearch, getFirstPos, imgShow, dispPoints, overlayPoints, getRealPoints, isEnd, plotPixelHist, getApproxTurn
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
    motorControl.speed(80)

    # declare vars to store image
    img = None
    greyImg = None
    data = None
    points = None
    rPoints = None

    def outputs():
        stream = io.BytesIO()
        i = 0
        lastTurn = 0
        timer = Timer([
            'got image array',
            'got image from array',
            'filtered image',
            'got grayscale image array',
            'got line points',
            'transformed points',
            'filtered points',
            'got approximate turn',
            'did turn'])
        maxY = pnt.transform((25,0))[1] - 10
        print('max Y: {}'.format(maxY))
        # return
        while True:
        # for i in range(40):
            yield stream
            # print('took picture {}'.format(i))
            # nonlocal img, greyImg, data, points, rPoints
            timer.reset()
            # format pixels as array
            imgArr = []
            stream.seek(0)
            with stream.getbuffer() as view:
                # img = Image.frombytes('RGB', (width, height), stream)
                imgArr = np.array(view)
                imgArr = imgArr.reshape(height, width, 3)
            timer.tick()
            img = Image.fromarray(imgArr, 'RGB')
            timer.tick()
            greyImg = picUtils.imgFilter(img, threshold)
            stopData = picUtils.getImgArray(greyImg)
            if picUtils.isEnd(stopData):
                print('Is End {}'.format(i))
                return
            img = img.resize((50, 50), Image.ANTIALIAS)
            greyImg = picUtils.imgFilter(img, threshold)
            data = picUtils.getImgArray(greyImg)

            points = picUtils.fillSearch(data, picUtils.getFirstPos(data))
            timer.tick()
            if points != None:
                points = pnt.transformPoints(points)
                timer.tick()
                points = pnt.filterPoints(points, 4)
                timer.tick()
                # a, count = picUtils.getApproxPointTurn(points, maxY)
                # timer.tick()
                # if count > 2:
                #     # convert average x to a turn value
                #     a = 0.00937815*a - 0.123739
                #     lastTurn = min(1, max(-1, a))
                a = picUtils.getTurn(points, maxY)
                # convert a
                a = 0.444*(a-0.287)
                lastTurn = min(1, max(-1, a))
                # print(a)
                # print('approx: {}, {}, {}'.format(a, count, lastTurn))
            # else:
            #     # print('No Points')
            #     pass
            # # print('last turn: {}'.format(lastTurn))
            # print(lastTurn)
            servoControl.turn(lastTurn)
            timer.tick()
            # print(timer)
            # # points = fillSearch(data, getFirstPos(data))
            # # if points == None:
            # #     print('No Starting Point {}'.format(i))
            # i += 1
            # motorControl.speed(100)
            # rPoints = getRealPoints(points)

            # img.save('homography.png', 'PNG')

            stream.seek(0)
            stream.truncate()

    print('starting captures')
    start = time()
    try:
        camera.capture_sequence(outputs(), 'rgb', use_video_port=True)
    finally:
        print('Closing Camera')
        camera.close()
        motorControl.speed(0)
    finish = time()

    # print('Captured {} images at {}fps'.format(
    #     nFrames,
    #     nFrames/(finish - start)))
    # imgShow(img)
    # imgShow(greyImg)
    # imgShow(data)
    # overlayPoints(img, points)
    # dispPoints(rPoints)

main()

# take the pic
#for i in range(10):
#    camera.capture('img' + str(i) + '.jpg', resize=(100,100))
