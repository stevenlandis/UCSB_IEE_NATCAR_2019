import camSetup
import io
import numpy as np
from PIL import Image
import homography
import picUtils
from threshold import threshold
import points as pnt
import servoControl

def main():
    while True:
        print('Choose an option to calibrate:')
        print('h: Homography')
        print('b: Brightness')
        print('s: Steering')
        print('q: Quit')
        val = input('choice: ')
        if val == 'h': runHomography()
        elif val == 'b': runThreshold()
        elif val == 's': runSteering()
        elif val == 'q': return

def takePic(path):
    camera = camSetup.init()
    width = camera.resolution.width
    height = camera.resolution.height

    def outputs():
        stream = io.BytesIO()
        yield stream
        imgArr = []
        stream.seek(0)
        with stream.getbuffer() as view:
            imgArr = np.array(view)
            imgArr = imgArr.reshape(height, width, 3)

        img = Image.fromarray(imgArr, 'RGB')
        img = img.resize((50, 50), Image.ANTIALIAS)
        img.save(path,'PNG')
        stream.seek(0)
        stream.truncate()

    camera.capture_sequence(outputs(), 'rgb', use_video_port=True)
    camera.close()

def runHomography():
    print('Position homography calibration sheet and press enter')
    input()
    takePic('homography.png')
    points = homography.GetPoints().run()
    H = homography.solveHomography(points, homography.REAL_POINTS)
    H_inv = homography.solveHomography(homography.REAL_POINTS, points)
    with open('H.py','w') as f:
        f.write('H = {}\nH_inv = {}'.format(
            H, H_inv))

def runThreshold():
    print('Move car to track and press enter')
    input()
    takePic('threshold.png')
    picUtils.plotPixelHist('threshold.png')
    print('Enter new threshold: ', end='')
    val = input()
    threshold = int(val)
    with open('threshold.py', 'w') as f:
        f.write('threshold = {}'.format(threshold))

    print('Test the threshold? [y/n] ',end='')
    val = input()
    if val != 'y': return

    while True:
        img = Image.open('threshold.png')
        img = img.resize((50, 50), Image.ANTIALIAS)
        img = picUtils.imgFilter(img, threshold)
        picUtils.imgShow(img)
        print('New threshold (0 to exit): ',end='')
        threshold = int(input())
        if threshold == 0: break
        with open('threshold.py', 'w') as f:
            f.write('threshold = {}'.format(threshold))

def runSteering():
    print('press enter to get average x: ',end='')
    input()
    avX = None
    takePic('steering.png')
    img = Image.open('steering.png')
    img = img.resize((50, 50), Image.ANTIALIAS)
    greyImg = picUtils.imgFilter(img, threshold)
    data = picUtils.getImgArray(greyImg)
    points = picUtils.fillSearch(data, picUtils.getFirstPos(data))
    if points == None:
        print('No Points Detected!')
        return
    points = pnt.transformPoints(points)
    points = pnt.filterPoints(points, 4)
    turn = picUtils.getTurn(points, 30)
    print('Turn: {}'.format(turn))

    servoControl.init()
    lo = -1
    hi = 1
    m = None
    while True:
        m = (lo+hi)/2
        servoControl.turn(m)
        print('left(l), right(r), or good(g)? ', end='')
        val = input()
        if val == 'g': break
        elif val == 'l': lo = m
        elif val == 'r': hi = m
    print('Turn {} was good'.format(m))

    with open('turnPoints.csv', 'a+') as f:
        f.write('{}, {}\n'.format(turn, m))
main()
