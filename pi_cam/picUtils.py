from PIL import Image, ImageDraw, ImageOps
import numpy as np
from ScannerRect import ScannerRect
import math
import matplotlib.pyplot as plt
import points as pnt
import servoControl

def main():
    threshold = 107

    img = Image.open('zigzag.png')
    img = ImageOps.grayscale(img)

    # threshold
    img = img.point(lambda p: p > threshold and 255)

    # get the pixel data
    data = np.array(img)

    print('img: {}, {}, data: {}'.format(
        img.width,img.height,data.shape))

    xSum = 0
    xCount = 0
    for x in range(0,img.width,1):
        for y in range(0,img.height,1):
            if data[y][x]:
                xSum += x
                xCount += 1
    print(2*xSum/xCount/img.width-1)

    # draw some lines
    draw = ImageDraw.Draw(img)

    points = fillSearch(data, getFirstPos(data))
    draw.line(points, fill=128)

    plt.imshow(img)
    plt.show()

    points = pnt.transformPoints(points)
    # dispPoints(points)

    points = pnt.filterPoints(points, 2*2)
    # dispPoints(points)

    pnt.smoothPoints(points, math.pi/2, 10)
    dispPoints(points)

    circles = pnt.getCircles(points, math.pi/2)
    pnt.dispCircles(circles)

def getRealPoints(pnts):
    pnts = pnt.transformPoints(pnts)
    pnts = pnt.filterPoints(pnts, 2*2)
    pnt.smoothPoints(pnts, math.pi/2, 10)
    return pnts

def plotPixelHist(imgPath):
    img = Image.open(imgPath)
    img = ImageOps.grayscale(img)
    data = np.array(img.getdata())
    plt.hist(data)
    plt.title('Intensity plot for "{}"'.format(imgPath))
    plt.show()

def imgFilter(img, threshold):
    img = ImageOps.grayscale(img)
    return img.point(lambda p: p > threshold and 255)

def getImgArray(img):
    return np.array(img)

def getApproxTurn(data):
    xSum = 0
    xCount = 0
    for x in range(0,data.shape[1],1):
        for y in range(0,data.shape[0],1):
            if data[y][x]:
                xSum += x
                xCount += 1
    # get expected x and scale to be within [-1, 1]
    if xCount == 0:
        return (None, 0)
    return (2*xSum/xCount/data.shape[1]-1, xCount)

# get the lowest point
def bottomPoints(data,lastX):
    halfWidth = data.shape[1]//2

    # scan botton
    for i in range(halfWidth):
        yield (halfWidth - i - 1, data.shape[0]-1)
        yield (halfWidth + i, data.shape[0]-1)

    # scan sides
    for i in range(data.shape[0]//2):
        yield (0, data.shape[0]-1-i)
        yield (data.shape[1]-1, data.shape[0]-1-i)

# get the lowest point
def bottomPoints2(data,startX):
    width = data.shape[1]
    height = data.shape[0]
    halfWidth = width//2

    # scan bottom
    if startX < halfWidth:
        for i in range(startX):
            yield (startX - i - 1, height-1)
            yield (startX + i, height-1)
        for i in range(width - 2*startX):
            yield (2*startX+i, height-1)
    else:
        for i in range(width - startX):
            yield (startX - i - 1, height-1)
            yield (startX + i, height-1)
        for i in range(2*startX - width):
            yield (2*startX - width - i - 1, height-1)
    return
    # scan sides
    for i in range(height//2):
        yield (0, height-1-i)
        yield (width-1, height-1-i)

def getFirstPos(data,lastX):
    for p in bottomPoints2(data,lastX):
        if data[p[1]][p[0]]:
            # print(x)
            return p
    return None

# detect if end of path in picture
def isEnd(data):
    width = data.shape[1]
    height = data.shape[0]
    state = 0
    dists = []
    for x in range(width):
        if state == 0:
            # no positive pixel found
            if data[height-1][x]:
                state = 1
                dists.append(0)
        elif state == 1:
            # last pixel was 1
            dists[-1] += 1
            if not data[height-1][x]:
                state = 2
                dists.append(0)
        elif state == 2:
            # last pixel was 0
            dists[-1] += 1
            if data[height-1][x]:
                state = 1
                dists.append(0)
    if state == 2:
        # remove empty from dist list
        dists.pop()
    res = len([d for d in dists if d >= 6]) == 5
    # if res:
    #     print(dists)
    #     # imgShow(data)
    return res

def around(x, y, w, h):
    if x > 0:
        yield (x-1, y)
    if y > 0:
        yield (x, y-1)
    if x+1 < w:
        yield (x+1, y)
    if y+1 < h:
        yield (x, y+1)

def fillSearch(data, p0, lastTurn):
    if p0 == None:
        return None
    points = []
    stack = [p0]
    data[p0[1]][p0[0]] = 0
    while len(stack):
        xSum = 0
        ySum = 0
        for p in stack:
            xSum += p[0]
            ySum += p[1]
        points.append((xSum//len(stack), ySum//len(stack)))

        # print(stack)
        dists = []
        for i in range(len(stack)-1):
            a = stack[i]
            b = stack[i+1]
            dx = a[0] - b[0]
            dy = a[1] - b[1]
            dist = dx*dx+dy*dy
            if dist > 3*3:
                dists.append((i, dist))
        # print(dists)
        if len(dists) == 2:
            # print(dists)
            stack = stack[dists[0][0]+1 : dists[1][0]+1]
            # plt.imshow(data)
            # plt.show()
        elif len(dists) == 1 and dists[0][1] > 12*12:
            if lastTurn < 0:
                print('left')
                stack = stack[:dists[0][0]+1]
            else:
                print('right')
                stack = stack[dists[0][0]+1:]

        nextStack = []
        while len(stack):
            top = stack.pop(0)
            for x1, y1 in around(top[0], top[1], data.shape[1], data.shape[0]):
                if data[y1][x1]:
                    data[y1][x1] = 0
                    nextStack.append((x1, y1))
                    xSum += x1
                    ySum += y1
        stack = nextStack

    # discard points after path gets too high
    maxI = 0
    while maxI < len(points):
        if points[maxI][1] < 7:break
        maxI+=1

    return points[:maxI]

def dispPoints(pnts):
    pnts = np.array(pnts)
    plt.scatter(pnts[:,0],pnts[:,1])
    plt.axes().set_aspect('equal')
    plt.show()

def getTurn(pts, maxY):
    i = 0
    while i < len(pts):
        if pts[i][1] > maxY:
            break
        i += 1
    xSum = 0
    ySum = 0
    nAv = min(i,5)
    if nAv == 0: return 0
    for j in range(nAv):
        xSum += pts[i-j-1][0]
        ySum += pts[i-j-1][1]
    ci = pnt.getCircleInfo((0,0),(xSum/nAv, ySum/nAv), math.pi/2)
    return -servoControl.getTurn(ci.r)

def getApproxPointTurn(pts, maxY):
    if pts == None:
        return (None, 0)
    xSum = 0
    nPts = 0
    for p in pts:
        if p[1] > maxY:
            break
        xSum += p[0] * p[1]
        nPts += 1
    if nPts == 0:
        return (None, 0)
    return (xSum/nPts, nPts)

def imgShow(img):
    plt.imshow(img)
    plt.show()

def overlayPoints(img, pnts):
    draw = ImageDraw.Draw(img)
    draw.line(pnts, fill=128)
    plt.imshow(img)
    plt.show()

# main()