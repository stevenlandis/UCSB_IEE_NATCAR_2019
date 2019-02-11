from PIL import Image
import numpy as np
from ScannerRect import ScannerRect
import math

threshold = 107

img = Image.open('img.jpg')

# threshold
img = img.point(lambda p: p > threshold and 255).convert('L')

s = ScannerRect(2, 4, 0, 0, 0)
s.scan(lambda x,y: print(x,y), 1, 0, math.pi/2, 112, 112, 1)