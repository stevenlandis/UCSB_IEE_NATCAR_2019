import math
# def timed_function(f, *args, **kwargs):
#     myname = str(f).split(' ')[1]
#     def new_func(*args, **kwargs):
#         t = utime.ticks_us()
#         result = f(*args, **kwargs)
#         delta = utime.ticks_diff(utime.ticks_us(), t)
#         print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
#         return result
#     return new_func
def getM(p0,p1):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    if dy == 0:
        if dx == 0:
            return 0
        else:
            return None
    else:
        return dx/dy
def getLine(p0, p1):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    m = None
    if dy != 0:
        m = dx/dy
    return (p0[0], p0[1], p1[0], p1[1], m)
class ScannerRect:
    def __init__(self, w, h, x, y, ang):
        self.w = w # rect width
        self.h = h # rect height
        self.x = x # central x
        self.y = y # central y
        self.ang = ang
    def scan(self, fcn, dx, dy, ang, width, height, step):
        totalAng = ang + self.ang
        minX = 0
        minY = 0
        maxX = width - 1
        maxY = height - 1
        cosa = math.cos(totalAng)
        sina = math.sin(totalAng)
        x0 = self.x * cosa - self.y * sina
        y0 = self.x * sina + self.y * cosa
        x0 += dx
        y0 += dy
        wx = -sina * self.w / 2
        wy = cosa * self.w / 2
        lx = cosa * self.h
        ly = sina * self.h
        pts = [
            (round(x0 + wx), round(y0 + wy)),
            (round(x0 - wx), round(y0 - wy)),
            (round(x0 - wx + lx), round(y0 - wy + ly)),
            (round(x0 + wx + lx), round(y0 + wy + ly))
        ]
        ys = [0]*4;
        minI = 0
        for i in range(len(pts)):
            ys[i] = pts[i][1]
            if pts[i][1] < pts[minI][1]:
                minI = i
        newPts = [
            pts[(minI + 0)%4],
            pts[(minI + 1)%4],
            pts[(minI + 2)%4],
            pts[(minI + 3)%4]
        ];
        pts = newPts
        ys.sort()
        ymin = max(minY, ys[0])
        ymax = min(maxY, ys[3])
        li = 0
        lm = getM(pts[0],pts[3])
        ri = 0
        rm = getM(pts[0],pts[1])
        for y in range(ymin, ymax+1, step):
            # print("At y =",y)
            # find the right line
            while y > pts[(ri+1)%4][1] or rm == None:
                # if ri == 2:
                #     print("Failed right with:")
                #     for p in pts:
                #         print(p[0],p[1])
                #     print("at y",y)
                ri = (ri+1)%4
                rm = getM(pts[ri],pts[(ri+1)%4])

            # find the left line
            while y > pts[(li-1)%4][1] or lm == None:
                # if li == 2:
                #     print("Failed left with:")
                #     for p in pts:
                #         print(p[0],p[1])
                #     print("at y",y)
                li = (li-1)%4
                lm = getM(pts[li],pts[(li-1)%4])

            lx = math.floor(pts[li][0] + lm * (y - pts[li][1]))
            rx = math. ceil(pts[ri][0] + rm * (y - pts[ri][1]))
            # print("Looping from",lx,"to",rx)
            lx = max(minX, lx)
            rx = min(maxX, rx)
            # do the loop
            for x in range(lx, rx + 1, step):
                fcn(x, y)