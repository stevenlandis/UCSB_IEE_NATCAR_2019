# Functions for smoothing points and getting arcs
from math import sqrt, cos, sin, pi, atan2
from H import H, H_inv # homography matrixes

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

def getCircles(pts, ang):
    p0 = pts[0]
    p1 = pts[1]
    res = []
    for i in range(len(pts)-1):
        p0 = pts[i]
        p1 = pts[i+1]
        ci = getCircleInfo(p0,p1,ang)
        res.append(ci)
        ang = ci.df
    return res

def dispCircles(ci):
    print(', '.join([str(c.r) for c in ci]))

def smoothPoints(pnts, ang, n):
    for i in range(n):
        nextPoints(pnts,ang)

def getFirstRadius(pnts, ang):
    if len(pnts) < 3: return 0

    ci = CircleInfo(pnts[0],pnts[1],ang)
    return ci.r

# Homography transformation
# H = [
#     0.3433119933772739,
#     -0.00013262148356181502,
#     -17.137219467110896,
#     0.007918201968029948,
#     -0.14752348892312117,
#     36.585824759039916,
#     0.0003959100984015085,
#     0.015061359048216125]
def transform(p):
    x,y = p
    scale = H[6]*x+H[7]*y+1
    return (
        (H[0]*x+H[1]*y+H[2])/scale,
        (H[3]*x+H[4]*y+H[5])/scale)

def invTransform(p):
    x,y = p
    scale = H_inv[6]*x+H_inv[7]*y+1
    return (
        (H_inv[0]*x+H_inv[1]*y+H_inv[2])/scale,
        (H_inv[3]*x+H_inv[4]*y+H_inv[5])/scale)

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
