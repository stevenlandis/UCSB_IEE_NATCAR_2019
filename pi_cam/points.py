# Functions for smoothing points and getting arcs
from math import sqrt, cos, sin, pi, atan2

class CircleInfo:
    def __init__(self):
        self.cx = None # center x
        self.cy = None # center y
        self.mx = None # middle x
        self.my = None # middle y
        self.md = None # direction at middle of arc
        self.r  = None # radius
        self.a0 = None # start angle
        self.a1 = None # end angle
        self.df = None # final direction

def getCircleInfo(p0, p1, ang):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]

    # rotate the points with ang along +x axis
    ang_cos = cos(-ang)
    ang_sin = sin(-ang)

    # find rotated x' and y'
    xp = ang_cos*dx - ang_sin*dy
    yp = ang_sin*dx + ang_cos*dy

    # center x' and y'
    cxp = 0
    cyp = (xp*xp + yp*yp)/(2*yp);
    r = cyp

    # end direction
    endAng = ang + pi/2 + atan2((yp*yp - xp*xp)/(2*yp), xp)
    if r < 0:
        endAng += pi

    # rotate and shift center x' and y' back
    ang_sin = -ang_sin
    cx = p0[0] + ang_cos*cxp - ang_sin*cyp
    cy = p0[1] + ang_sin*cxp + ang_cos*cyp

    # get start angles
    dx = p0[0] - cx
    dy = p0[1] - cy
    a0 = atan2(dy, dx)

    # get end angle
    dx = p1[0] - cx;
    dy = p1[1] - cy;
    a1 = atan2(dy, dx);

    # if r < 0, swap start and end
    if r < 0:
        temp = a0
        a0 = a1
        a1 = temp

    # shift a1 up so it is larger than a0
    while a0 > a1:
        a1 += 2*pi

    # shift a1 down just above a0
    while a1 > a0 + 2*pi:
        a1 -= 2*pi

    # angle of middle of arc
    ma = (a0 + a1)/2
    if r < 0:
        ma += pi

    # direction at middle of arc
    md = ma + pi/2

    # get coords of middle of arc
    mx = cx + r * cos(ma)
    my = cy + r * sin(ma)

    res = CircleInfo()
    res.cx = cx
    res.cy = cy
    res.mx = mx
    res.my = my
    res.md = md
    res.r  = r
    res.a0 = a0
    res.a1 = a1
    res.df = endAng
    return res;

# smooth points
# the magic function
# ang is initial direction
def nextPoints(pts, ang):
    for i in range(len(pts)-2):
        p0 = pts[i]
        p1 = pts[i+1]
        p2 = pts[i+2]

        # get arc info
        ci = getCircleInfo(p0, p2, ang)

        # get new next coordinate for p1
        newPt = (
            (ci.mx+p1[0])/2,
            (ci.my+p1[1])/2)
        pts[i+1] = newPt

        # use direction at center for next line
        ang = ci.md

def smoothPoints(pnts, ang, n):
    for i in range(n):
        nextPoints(pnts,ang)

def getFirstRadius(pnts, ang):
    if len(pnts) < 3: return 0

    ci = CircleInfo(pnts[0],pnts[1],ang)
    return ci.r

# Homography transformation
# H = [0.07746203773260954, 0.0026592742006694894, -20.79510858690768, -5.857577974861805e-05, -0.03356021614233259, 33.599693587262415, -0.00062404541481389, 0.0048092072848485955]
H = [0.33311589978029765, 0.011487973508034086, -20.129251262460045, 0.004165417405152083, -0.15981606350352603, 33.00375144957151, -0.0023951082540435396, 0.01963394197713035]
def transform(p):
    x,y = p
    scale = H[6]*x+H[7]*y+1
    return (
        (H[0]*x+H[1]*y+H[2])/scale,
        (H[3]*x+H[4]*y+H[5])/scale)

def transformPoints(pts):
    return [transform(p) for p in pts]

def dist2(p0, p1):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    return dx*dx+dy*dy

def filterPoints(pts, minDist2):
    remove = [False]*len(pts)

    # mark points for removal
    lastPnt = 0
    for i in range(len(pts)-1):
        if dist2(pts[lastPnt], pts[i]) < minDist2:
            remove[i] = True
        else:
            lastPnt = i

    # do the removal
    return [pts[i] for i in range(len(pts)) if not remove[i]]