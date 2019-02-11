from PIL import Image, ImageDraw, ImageOps
import numpy as np
from ScannerRect import ScannerRect
import math
import matplotlib.pyplot as plt

def plotPixelHist(imgPath):
    img = Image.open(imgPath)
    img = ImageOps.grayscale(img)
    data = np.array(img.getdata())
    plt.hist(data)
    plt.title('Intensity plot for "{}"'.format(imgPath))
    plt.show()

threshold = 107

img = Image.open('img.jpg')
img = ImageOps.grayscale(img)

# threshold
img = img.point(lambda p: p > threshold and 255)

# get the pixel data
data = np.array(img)

xSum = 0
xCount = 0
for x in range(img.width):
    for y in range(img.height):
        if data[y][x]:
            xSum += x
            xCount += 1
print(2*xSum/xCount/img.width-1)

plt.imshow(data)
plt.show()
# img.show()

# s = ScannerRect(2, 4, 0, 0, 0)
# s.scan(lambda x,y: print(x,y), 1, 0, math.pi/2, 112, 112, 1)