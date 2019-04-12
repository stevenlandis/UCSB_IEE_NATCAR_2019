from PIL import Image, ImageDraw, ImageOps
import numpy as np
from ScannerRect import ScannerRect
import math
import matplotlib.pyplot as plt
import points as pnt

def plotPixelHist(imgPath):
    img = Image.open(imgPath)
    img = ImageOps.grayscale(img)
    data = np.array(img.getdata())
    plt.hist(data)
    plt.title('Intensity plot for "{}"'.format(imgPath))
    plt.show()

threshold = 107

img = Image.open('zigzag.png')
img = ImageOps.grayscale(img)

# threshold
img = img.point(lambda p: p > threshold and 255)

# get the pixel data
data = np.array(img)

xSum = 0
xCount = 0
for x in range(0,img.width,1):
    for y in range(0,img.height,1):
        if data[y][x]:
            xSum += x
            xCount += 1
print(2*xSum/xCount/img.width-1)

# plt.imshow(data)
# plt.show()
# img.show()

# get the lowest point
def bottomPoints():
    halfWidth = img.width//2

    # scan botton
    for i in range(halfWidth):
        yield (halfWidth - i - 1, img.height-1)
        yield (halfWidth + i, img.height-1)

    # scan sides
    for i in range(img.height//2):
        yield (0, img.height-1-i)
        yield (img.width-1, img.height-1-i)

def getFirstPos(data):
    for p in bottomPoints():
        if data[p[1]][p[0]]:
            # print(x)
            return p
    return None

# x = getFirstPos(data)

def around(x, y, w, h):
    if x > 0:
        yield (x-1, y)
    if y > 0:
        yield (x, y-1)
    if x+1 < w:
        yield (x+1, y)
    if y+1 < h:
        yield (x, y+1)

def fillSearch(data, p0):
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
            if dist > 100:
                dists.append((i, dist))
        if len(dists) == 2:
            print(dists)
            stack = stack[dists[0][0]+1 : dists[1][0]+1]
            plt.imshow(data)
            plt.show()

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
    return points

def dispPoints(pnts):
    pnts = np.array(pnts)
    plt.scatter(pnts[:,0],pnts[:,1])
    plt.axes().set_aspect('equal')
    plt.show()

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