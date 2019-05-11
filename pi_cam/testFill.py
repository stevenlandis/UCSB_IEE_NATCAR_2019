from PIL import Image
import picUtils
from threshold import threshold

img = Image.open('test.png')
greyImg = picUtils.imgFilter(img, threshold)
data = picUtils.getImgArray(greyImg)
p0 = picUtils.getFirstPos(data, 25)
points = picUtils.fillSearch(data, p0, 0)