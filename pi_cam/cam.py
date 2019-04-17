from picamera import PiCamera
from time import sleep, time
import io
from PIL import Image
import numpy as np
from picUtils import imgFilter, getImgArray, fillSearch, getFirstPos, imgShow, dispPoints, overlayPoints, getRealPoints, isEnd, plotPixelHist

def main():
    # width = 64
    # height = 64
    # width = 1920
    # height = 1088
    plotPixelHist('homography.png')
    return
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

    # # set camera settings
    # camera.resolution = (width, height)
    # camera.framerate = 80

    # camera.start_preview()
    # sleep(100)
    # camera.stop_preview()
    # return

    # allow two seconds for camera sensors to adjust
    sleep(2)
    print('Camera adjusted')

    nFrames = 40

    # declare vars to store image
    img = None
    greyImg = None
    data = None
    points = None
    rPoints = None

    # set up 40 memory streams
    def outputs():
        stream = io.BytesIO()
        # for i in range(nFrames):
        i = 0
        while True:
            yield stream

            # print('took picture {}'.format(i))

            nonlocal img, greyImg, data, points, rPoints

            # format pixels as array
            imgArr = []
            stream.seek(0)
            with stream.getbuffer() as view:
                # img = Image.frombytes('RGB', (width, height), stream)
                imgArr = np.array(view)
                imgArr = imgArr.reshape(height, width, 3)

            img = Image.fromarray(imgArr, 'RGB')
            greyImg = imgFilter(img, 200)
            data = getImgArray(greyImg)
            if isEnd(data):
                print('Is End {}'.format(i))
            points = fillSearch(data, getFirstPos(data))
            if points == None:
                print('No Starting Point {}'.format(i))
            i += 1
            # rPoints = getRealPoints(points)

            # img.save('homography.png', 'PNG')

            # for j in range(width*height//2):
            #     if j % width == 0:
            #         imgArr.append([])
            #     r=int(stream.read(1)[0])
            #     g=int(stream.read(2)[0])
            #     b=int(stream.read(3)[0])
            #     imgArr.append(r)
            #     imgArr.append(g)
            #     imgArr.append(b)
            # # print(imgArr)
            
            # img = Image.fromarray(imgArr, 'RGB')        
            # # save to file
            # stream.seek(0)
            # with open('img.rgb', 'wb') as out:
            #     out.write(stream.read())

            # stream.seek(0)
            # try:
            #     for j in range(width*height//2):
            #         r=int(stream.read(1)[0])
            #         g=int(stream.read(2)[0])
            #         b=int(stream.read(3)[0])
            #         # print(j,r,g,b)
            # except:
            #     print('Failed on {}'.format(j))

            #print(stream.read(10))

            stream.seek(0)
            stream.truncate()

    print('starting captures')
    start = time()
    camera.capture_sequence(outputs(), 'rgb', use_video_port=True)
    finish = time()

    print('Captured {} images at {}fps'.format(
        nFrames,
        nFrames/(finish - start)))
    # imgShow(img)
    # imgShow(greyImg)
    # imgShow(data)
    # overlayPoints(img, points)
    # dispPoints(rPoints)

main()

# take the pic
#for i in range(10):
#    camera.capture('img' + str(i) + '.jpg', resize=(100,100))
