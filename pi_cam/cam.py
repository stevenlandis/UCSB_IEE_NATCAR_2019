from picamera import PiCamera
from time import sleep, time
import io
from PIL import Image
import numpy as np
from picUtils import imgFilter, getImgArray, fillSearch, getFirstPos, imgShow

# width = 112
# height = 112
width = 1920
height = 1088

camera = PiCamera()

# set cameral settings
camera.resolution = (width, height)
camera.framerate = 80

# allow two seconds for camera sensors to adjust
sleep(2)
print('Camera adjusted')

# set up 40 memory streams
def outputs():
    stream = io.BytesIO()
    for i in range(1):
        yield stream

        print('took picture {}'.format(i))

        # format pixels as array
        imgArr = []
        stream.seek(0)
        with stream.getbuffer() as view:
            # img = Image.frombytes('RGB', (width, height), stream)
            imgArr = np.array(view)
            imgArr = imgArr.reshape(width, height, 3)

        img = Image.fromarray(imgArr, 'RGB')
        imgShow(img)
        img = imgFilter(img, 107)
        data = getImgArray(img)
        points = fillSearch(data, getFirstPos(data))

        # img.save('img.jpg', 'JPEG')

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

print('Captured 40 images at {}fps'.format(
    40/(finish - start)    
))

# take the pic
#for i in range(10):
#    camera.capture('img' + str(i) + '.jpg', resize=(100,100))
